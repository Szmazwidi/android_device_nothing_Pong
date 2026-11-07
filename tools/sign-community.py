#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Sign complete target-files and an OTA with private maintainer identities.

PRESIGNED applications and APEXes retain their vendor identities. No phone access.
The signed result requires separate data/signing-migration qualification.
"""
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import tempfile
import zipfile


def run(argv, **kwargs):
    return subprocess.check_output(list(map(str, argv)), stderr=subprocess.PIPE, timeout=180, **kwargs)


def records(text):
    return [dict(token.split('=', 1) for token in shlex.split(line))
            for line in text.splitlines() if line.strip() and not line.startswith('#')]


def source_path(root, name):
    path = (root / name).resolve()
    if not path.is_relative_to(root):
        raise ValueError('Signing metadata points outside the Android source root')
    return path


def certificate_digest(path):
    return hashlib.sha256(run(['openssl', 'x509', '-in', path, '-outform', 'DER'])).hexdigest()


def save_backup(path, keys, backup):
    target = backup / path.relative_to(keys)
    target.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    if target.exists() and target.read_bytes() != path.read_bytes():
        raise ValueError('Existing signing-key backup differs')
    if not target.exists():
        shutil.copyfile(path, target)
    target.chmod(0o600)


def identity(prefix, keys, backup):
    prefix.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    private, pk8, cert = [prefix.with_name(prefix.name + suffix) for suffix in ('.pem', '.pk8', '.x509.pem')]
    if not any(path.exists() for path in (private, pk8, cert)):
        run(['openssl', 'genpkey', '-algorithm', 'RSA', '-pkeyopt', 'rsa_keygen_bits:4096', '-out', private])
        run(['openssl', 'pkcs8', '-topk8', '-nocrypt', '-in', private, '-outform', 'DER', '-out', pk8])
    if not private.is_file() or not pk8.is_file():
        raise ValueError('Partial existing signing identity requires inspection')
    public = run(['openssl', 'pkey', '-in', private, '-pubout', '-outform', 'DER'])
    if public != run(['openssl', 'pkey', '-inform', 'DER', '-in', pk8, '-pubout', '-outform', 'DER']):
        raise ValueError('Private key and PKCS8 key do not match')
    if not cert.exists() or cert.stat().st_size == 0:
        common_name = 'Pong release ' + prefix.name
        if len(common_name) > 64:
            common_name = common_name[:47] + '-' + hashlib.sha256(common_name.encode()).hexdigest()[:16]
        run(['openssl', 'req', '-new', '-x509', '-sha256', '-key', private, '-out', cert,
             '-days', '10000', '-subj', '/O=Szmazwidi/CN=' + common_name])
    if run(['openssl', 'x509', '-in', cert, '-pubkey', '-noout']) != run(['openssl', 'pkey', '-in', private, '-pubout']):
        raise ValueError('Private key and certificate do not match')
    for path in (private, pk8, cert):
        path.chmod(0o600)
        save_backup(path, keys, backup)
    return certificate_digest(cert)


def sign(args):
    root = args.android.resolve()
    keys, backup = args.keys.resolve(), args.backup.resolve()
    args.output.mkdir(mode=0o700, parents=True, exist_ok=False)
    args.work.mkdir(mode=0o700, parents=True, exist_ok=True)
    host = root / 'out/host/linux-x86/bin'
    env = dict(os.environ, JAVA_HOME=str(root / 'prebuilts/jdk/jdk21/linux-x86'),
               ANDROID_HOST_OUT=str(host.parent), TMPDIR=str(args.work.resolve()))
    env['PATH'] = str(host) + ':' + env['JAVA_HOME'] + '/bin:' + env.get('PATH', '')
    selected_apks = set()
    selected_apexes = []
    presigned = []
    mappings = {}
    preserved_copy_files = []
    with zipfile.ZipFile(args.target_files) as source, tempfile.TemporaryDirectory(dir=args.work) as temp:
        temp = Path(temp)
        apk_rows = {row['name']: row for row in records(source.read('META/apkcerts.txt').decode())}
        apex_rows = {row['name']: row for row in records(source.read('META/apexkeys.txt').decode())}
        for name in source.namelist():
            if name.endswith(('.apk', '.apk.gz')):
                selected_apks.add(Path(name).name.removesuffix('.gz'))
            if not name.endswith(('.apex', '.capex')):
                continue
            apex_name = Path(name).name.removesuffix('.capex').removesuffix('.apex') + '.apex'
            row = apex_rows[apex_name]
            if row['container_certificate'] == 'PRESIGNED':
                presigned.append(apex_name)
                continue
            selected_apexes.append(row)
            apex = temp / 'current.apex'
            apex.write_bytes(source.read(name))
            if name.endswith('.capex'):
                unpacked = temp / 'uncompressed.apex'
                run([host / 'deapexer', 'decompress', '--input', apex, '--output', unpacked], env=env)
                apex = unpacked
            listing = run([host / 'deapexer', '--debugfs_path', host / 'debugfs_static',
                           '--fsckerofs_path', host / 'fsck.erofs', 'list', apex], env=env).decode()
            selected_apks.update(Path(line.strip()).name for line in listing.splitlines()
                                 if line.strip().endswith('.apk'))
            if (temp / 'uncompressed.apex').exists():
                (temp / 'uncompressed.apex').unlink()
        prefixes = set()
        for name in selected_apks:
            if name not in apk_rows:
                # GMS declares these compressed blobs with PRODUCT_COPY_FILES,
                # not android_app_import. Keep Google's verified signer.
                if name not in ('Chrome.apk', 'TrichromeLibrary.apk', 'WebViewGoogle.apk'):
                    raise ValueError('Unknown APK without signing metadata: ' + name)
                directory = name.removesuffix('.apk')
                relative = 'product/app/' + directory + '/' + name + '.gz'
                packaged = 'PRODUCT/' + relative.removeprefix('product/')
                origin = root / 'vendor/pixel/gms/common/proprietary' / relative
                declaration = 'vendor/pixel/gms/common/proprietary/' + relative + ':$(TARGET_COPY_OUT_PRODUCT)/' + relative.removeprefix('product/')
                makefile = (root / 'vendor/pixel/gms/common/common-vendor.mk').read_text()
                data = source.read(packaged)
                if declaration not in makefile or data != origin.read_bytes():
                    raise ValueError('GMS copied APK does not match its source declaration')
                decoded = temp / name
                decoded.write_bytes(gzip.decompress(data))
                verification = run([host / 'apksigner', 'verify', '--print-certs', decoded], env=env).decode()
                preserved_copy_files.append({'file': packaged, 'source': str(origin),
                    'sha256': hashlib.sha256(data).hexdigest(), 'signature_verification': verification})
                apk_rows[name] = {'name': name, 'certificate': 'PRESIGNED'}
            row = apk_rows[name]
            if row['certificate'] in ('PRESIGNED', 'EXTERNAL'):
                presigned.append(name)
                continue
            prefixes.add(row['certificate'].removesuffix('.x509.pem'))
        for row in selected_apexes:
            prefixes.add(row['container_certificate'].removesuffix('.x509.pem'))
        # Preserve signer equivalence across different source paths.
        by_old_digest = {}
        for name in ('testkey', 'platform', 'shared', 'media', 'networkstack', 'bluetooth', 'nfc', 'sdk_sandbox'):
            old = root / 'build/make/target/product/security' / (name + '.x509.pem')
            dest = keys / ('releasekey' if name == 'testkey' else name)
            if old.exists() and dest.with_suffix('.x509.pem').exists():
                by_old_digest[certificate_digest(old)] = dest
        public_certificates = []
        for prefix in sorted(prefixes):
            old = source_path(root, prefix + '.x509.pem')
            old_digest = certificate_digest(old)
            dest = by_old_digest.get(old_digest)
            if dest is None:
                safe = re.sub('[^A-Za-z0-9_.-]', '_', Path(prefix).name)
                dest = keys / 'apk' / (safe + '-' + old_digest[:12])
                by_old_digest[old_digest] = dest
            digest = identity(dest, keys, backup)
            mappings[prefix] = str(dest)
            public_certificates.append({'old_certificate_sha256': old_digest, 'new_certificate_sha256': digest})
        arguments = []
        for row in preserved_copy_files:
            arguments.extend(['--extra_apks', Path(row['file']).name.removesuffix('.gz') + '='])
        for src, dst in sorted(mappings.items()):
            arguments.extend(['-k', src + '=' + dst])
        for row in selected_apexes:
            dest = keys / 'apex' / row['name'].removesuffix('.apex')
            dest.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
            key = dest.with_name(dest.name + '.pem')
            if not key.exists():
                run(['openssl', 'genpkey', '-algorithm', 'RSA', '-pkeyopt', 'rsa_keygen_bits:4096', '-out', key])
            key.chmod(0o600)
            save_backup(key, keys, backup)
            arguments.extend(['--extra_apex_payload_key', row['name'] + '=' + str(key)])
        signed = args.output.resolve() / 'signed-target_files.zip'
        for partition in ('vbmeta', 'recovery', 'vbmeta_system', 'vbmeta_vendor'):
            alias = {'vbmeta': 'avb', 'recovery': 'avb_recovery',
                     'vbmeta_system': 'avb_system', 'vbmeta_vendor': 'avb_vendor'}[partition]
            private = keys / (alias + '.pem')
            if not private.exists():
                raise ValueError('Missing private AVB release identity')
            save_backup(private, keys, backup)
            arguments.extend(['--avb_' + partition + '_key', str(private),
                              '--avb_' + partition + '_algorithm', 'SHA256_RSA4096'])
        arguments.extend(['--avb_vbmeta_extra_args', '--flags 0'])
        # AOSP -o remaps the device OTA certificates and A/B payload verification key.
        command = [host / 'sign_target_files_apks', '-o', '-d', keys, *arguments,
                   args.target_files.resolve(), signed]
        report = {'status': 'SIGNING_TARGET_FILES', 'profile': 'community',
                  'APK_migration_from_existing_test_keys_qualified': False,
                  'selected_APKs': len(selected_apks), 'resigned_APEXes': len(selected_apexes),
                  'preserved_PRESIGNED': sorted(presigned), 'public_certificates': public_certificates,
                  'preserved_copy_file_APKs': preserved_copy_files,
                  'phone_operations': 0}
        def save():
            (args.output / 'signing-report.json').write_text(json.dumps(report, indent=2) + '\n')
        save()
        with (args.output / 'sign-target-files.log').open('wb') as log:
            subprocess.run(list(map(str, command)), cwd=root, env=env, stdout=log, stderr=subprocess.STDOUT,
                           check=True, timeout=7200)
        with zipfile.ZipFile(signed) as checked:
            misc = dict(line.split('=', 1) for line in checked.read('META/misc_info.txt').decode().splitlines() if '=' in line)
            if '--flags 3' in misc.get('avb_vbmeta_args', '').split('--flags 0')[-1]:
                raise ValueError('Signed vbmeta still disables verification')
        report['status'] = 'BUILDING_SIGNED_OTA'
        save()
        ota = args.output.resolve() / 'DerpFest-Pong-6.18.60-community-candidate.zip'
        with (args.output / 'ota.log').open('wb') as log:
            subprocess.run([str(host / 'ota_from_target_files'), '-k', str(keys / 'releasekey'),
                            str(signed), str(ota)], cwd=root, env=env, stdout=log, stderr=subprocess.STDOUT,
                           check=True, timeout=7200)
        with ota.open('rb') as stream:
            report['ota_sha256'] = hashlib.file_digest(stream, 'sha256').hexdigest()
        ota.with_name(ota.name + '.sha256sum').write_text(report['ota_sha256'] + '  ' + ota.name + '\n')
        report.update(status='SIGNED_COMMUNITY_CANDIDATE_READY_NOT_FLASHED', signed_target_files=str(signed),
                      ota=str(ota), data_preserving_key_migration_tested=False)
        save()
        print(report['status'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('android', 'target-files', 'keys', 'backup', 'output', 'work'):
        parser.add_argument('--' + name, type=Path, required=True)
    args = parser.parse_args()
    os.umask(0o077)
    sign(args)


if __name__ == '__main__':
    main()
