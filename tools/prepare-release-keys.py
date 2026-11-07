#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Create maintainer signing identities privately and keep a verified backup."""
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

HERE = Path(__file__).resolve().parent
KEYS = None
BACKUP = None
NAMES = ['releasekey', 'platform', 'shared', 'media', 'networkstack', 'bluetooth', 'nfc', 'sdk_sandbox']


def call(args):
    subprocess.run(list(map(str, args)), check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, timeout=180)


def main():
    global KEYS, BACKUP
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--keys', type=Path, required=True)
    parser.add_argument('--backup', type=Path, required=True)
    args = parser.parse_args()
    KEYS, BACKUP = args.keys.resolve(), args.backup.resolve()
    if KEYS == BACKUP or KEYS.is_relative_to(BACKUP) or BACKUP.is_relative_to(KEYS):
        raise ValueError('Use separate key and backup directories')
    os.umask(0o077)
    KEYS.mkdir(mode=0o700, parents=True, exist_ok=True)
    BACKUP.mkdir(mode=0o700, parents=True, exist_ok=True)
    KEYS.chmod(0o700)
    BACKUP.chmod(0o700)
    outputs = []
    for name in NAMES:
        key, pk8, cert = (KEYS / (name + suffix) for suffix in ('.pem', '.pk8', '.x509.pem'))
        if any(p.exists() for p in (key, pk8, cert)):
            if not all(p.is_file() for p in (key, pk8, cert)):
                raise RuntimeError('Partial signing identity exists; preserve it for review')
        else:
            call(['openssl', 'genpkey', '-algorithm', 'RSA', '-pkeyopt', 'rsa_keygen_bits:4096', '-out', key])
            call(['openssl', 'pkcs8', '-topk8', '-inform', 'PEM', '-outform', 'DER', '-nocrypt', '-in', key, '-out', pk8])
            call(['openssl', 'req', '-new', '-x509', '-sha256', '-key', key, '-out', cert, '-days', '10000',
                  '-subj', '/O=Pong community/CN=Pong 6.18 ' + name])
        key_public = subprocess.check_output(['openssl', 'pkey', '-in', str(key), '-pubout', '-outform', 'DER'])
        cert_public = subprocess.check_output(['openssl', 'x509', '-in', str(cert), '-pubkey', '-noout'])
        decoded = subprocess.run(['openssl', 'pkey', '-pubin', '-outform', 'DER'], input=cert_public,
                                 check=True, capture_output=True).stdout
        if decoded != key_public:
            raise RuntimeError('Certificate/private key mismatch')
        der = subprocess.check_output(['openssl', 'x509', '-in', str(cert), '-outform', 'DER'])
        outputs.append({'name': name, 'certificate_sha256': hashlib.sha256(der).hexdigest()})
        for path in (key, pk8, cert):
            path.chmod(0o600)
            target = BACKUP / path.name
            if target.exists() and target.read_bytes() != path.read_bytes():
                raise RuntimeError('Signing backup already differs')
            if not target.exists():
                shutil.copyfile(path, target)
                target.chmod(0o600)
    # AVB identities remain separate from application signatures.
    for name in ('avb', 'avb_recovery', 'avb_system', 'avb_vendor'):
        key = KEYS / (name + '.pem')
        if not key.exists():
            call(['openssl', 'genpkey', '-algorithm', 'RSA', '-pkeyopt', 'rsa_keygen_bits:4096', '-out', key])
        key.chmod(0o600)
        target = BACKUP / key.name
        if target.exists() and target.read_bytes() != key.read_bytes():
            raise RuntimeError('Existing AVB backup differs')
        if not target.exists():
            shutil.copyfile(key, target)
            target.chmod(0o600)
    for path in KEYS.iterdir():
        if path.suffix in ('.pem', '.pk8'):
            target = BACKUP / path.name
            if not target.is_file() or target.read_bytes() != path.read_bytes():
                raise RuntimeError('Signing backup verification failed')
    report = {'status': 'PRIVATE_RELEASE_KEYS_CREATED_AND_BACKUP_VERIFIED',
              'created_at_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
              'private_directory': str(KEYS), 'backup_directory': str(BACKUP),
              'keys_encrypted': False, 'private_file_mode': '0600', 'directory_mode': '0700',
              'public_certificates': outputs, 'key_material_in_source_repository': False,
              'APK_APEX_migration_qualified': False, 'phone_operations': 0}
    (KEYS / 'public-certificates.json').write_text(json.dumps(report, indent=2) + '\n')
    print(report['status'])


if __name__ == '__main__':
    main()
