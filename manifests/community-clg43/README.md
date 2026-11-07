# Community CLG43: reproduce the qualified source cohort

Keep the original authors and license notices. The community branch derives from
CLG43 plus the selected CNSS2 CBC option. OTG/FSA experiments remain on separate
branches. The kernel module bank is built from source: 209 vendor and 84 GKI
modules, with forced SHA-256 signatures and no device-specific LAB admission.

## Complete Android source snapshot

Use an empty source directory and a separate support checkout:

```sh
git clone --branch pong-6.18-community-clg43 --single-branch \
  https://github.com/Szmazwidi/android_device_nothing_Pong.git pong-build-support
git -C pong-build-support rev-parse HEAD
mkdir android17
cd android17
repo init -u "$(cd ../pong-build-support && pwd)" -b pong-6.18-community-clg43 \
  -m manifests/community-clg43/full.xml --git-lfs --no-clone-bundle
repo sync -c -j4 --fail-fast
repo forall -c 'git lfs pull && git lfs fsck'
python3 ../pong-build-support/manifests/community-clg43/apply-snapshot.py --check
python3 ../pong-build-support/manifests/community-clg43/apply-snapshot.py
source build/envsetup.sh
lunch lineage_Pong-cp2a-user
export DERPFEST_BUILD_TYPE=Community DERPFEST_BETA=false
mka target-files-package -j4
```

The full manifest pins 1259 projects. Two captured local patches are required:
the current SELinux compatibility mapping and idempotent QTI boot-success handling.
The older `manifests/patches` bundle belongs to the earlier snapshot; use the
matching `community-clg43` bundle. Keep the support checkout outside the source
tree, because the pinned functional device commit predates these recipe files.

The current checkout completed this target-files build. Downloading all 1259
projects again in an empty checkout remains untested. Access to each repository
and proprietary/LFS dependencies is required; a private source repository must be
made accessible separately before announcing a public reproducible release.

## Kernel sources and signing

The kernel/module recipe and exact manifest are in the matching
`android_kernel_nothing_sm8475-modules-6.18` community branch:
`docs/COMMUNITY-CLG43.md` and `docs/manifest/pong618-6.18.60-community.xml`.
Import the resulting signed bank with `Pong-kernel/import-source-build.py` using
the explicit community reference; verify its `--check-only` result first.

Use maintainer-owned keys outside Git for APK/APEX, AVB and OTA signing. The local
release helper preserves explicitly PRESIGNED vendor identities, including the
three compressed GMS copy-file APKs after source-byte and signature checks.
The matching source tools are `tools/prepare-release-keys.py` and
`tools/sign-community.py`. They were exercised on the maintainer's actual
cohort, with an idempotent key-backup check and independent OTA verification.
Private keys are unencrypted and protected by directory mode 0700 / file mode
0600; choose private locations outside every Git checkout and protect their backup.

```sh
python3 ../pong-build-support/tools/prepare-release-keys.py \
  --keys /private/pong-keys --backup /separate-backup/pong-keys
python3 ../pong-build-support/tools/sign-community.py \
  --android "$PWD" \
  --target-files out/target/product/Pong/obj/PACKAGING/target_files_intermediates/lineage_Pong-target_files.zip \
  --keys /private/pong-keys --backup /separate-backup/pong-keys \
  --output /private/new-release-output --work /private/signing-work
```

The output directory must be new. Existing key identities are verified and
reused; they are never silently rotated. Keep PRESIGNED vendor identities.
The signed candidate is a separate installation identity. Existing developer-key
data must not be migrated merely by flashing it: package/shared-UID, APEX and OTA
trust migration require independent qualification.

## Hardware qualification boundary

The single available handset is an EEA Pong with 12 GB nominal RAM and 256 GB UFS.
Observed baseband: `-01026.2-WAIPIO_GEN_PACK-1.134215.10.142897.3`;
bootloader: `00979.4-WAIPIO-1`. These are observations, not a tested minimum firmware.

The current campaign preserves the owner's data. It does not qualify a factory
reset, fresh installation, other RAM/UFS variants or release-key migration. Keep
native ROM, rooted diagnostic and physical feature results separate.

## Recorded qualification

See [qualification.json](qualification.json) for the host, native Android and
physical checks, exact source cohort and remaining release gates. The tested
upgrade writes nine Android B images with the original APK identities; it does
not exercise a complete 13-partition signed OTA or replace recovery/vbmeta.
A separate RAM boot of the unmodified source boot image completed Android
without Magisk, then returned to the persistent rooted image.

The primary kernel, module, device and prebuilt repositories and manually
attached Pong dependencies were observed public on GitHub on 2026-11-07. The
manifest was also parsed by repo in an empty workspace. Full clean resync and
other hardware variants remain unqualified.

The short tethered sleep test is inconclusive: BatteryGuru holds a charging
wakelock, and the control after temporarily stopping it still yielded zero
CXSD/AOSD/DDR counts. The application was restarted. Do not substitute this
for an untethered standby test or report it as a power-management pass.
