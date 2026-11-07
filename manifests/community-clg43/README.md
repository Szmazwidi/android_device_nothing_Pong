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
Its signed candidate is a separate installation identity. Existing developer-key
data must not be migrated merely by flashing it: package/shared-UID, APEX and OTA
trust migration require independent qualification.

## Hardware qualification boundary

The single available handset is an EEA Pong with 12 GB nominal RAM and 256 GB UFS.
Observed baseband: `-01026.2-WAIPIO_GEN_PACK-1.134215.10.142897.3`;
bootloader: `00979.4-WAIPIO-1`. These are observations, not a tested minimum firmware.

The current campaign preserves the owner's data. It does not qualify a factory
reset, fresh installation, other RAM/UFS variants or release-key migration. Keep
native ROM, rooted diagnostic and physical feature results separate.
