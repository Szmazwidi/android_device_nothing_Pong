# Pong Android 17 / Linux 6.18.64 RC

This directory records the source recipe for the signed DerpFest community
candidate tested on 17 November 2026. The kernel is Linux 6.18.64 with the
retained Android 17 ACK and Pong adaptations. The full OTA uses the verified
16 November DerpFest userspace, with the matching 6.18.64 kernel and modules.

The tested kernel revision is
`febb385ea217722658e25cebffc2e79171be69c7`. The matching module revision is
`bc31a11678ace6bd8a2af7f33cf49278a169e201`. The functional device-tree
revision is `21b50a2352bd6203452ab57f201551a86c60b08e`.
[Qualification](qualification.json) records the host and device results.
[Attribution](ATTRIBUTION.md) records the source and contributor history.

## Kernel and all modules

Use Linux with the Android kernel build dependencies, `repo`, Git and an
AArch64 system QEMU. Keep the support checkout outside the build workspace.

```sh
git clone --single-branch --branch pong-6.18.64-community-rc \
  https://github.com/Szmazwidi/android_device_nothing_Pong.git pong-build-support
recipe="$(realpath pong-build-support/manifests/community-6.18.64-rc)"

mkdir pong-kernel-workspace
cd pong-kernel-workspace
repo init -u https://android.googlesource.com/kernel/manifest -b common-android17-6.18
cp "$recipe/kernel.xml" .repo/manifests/pong618.xml
repo init -m pong618.xml
repo sync -c -j4

export PONG_MANIFEST="$PWD/.repo/manifests/pong618.xml"
export PONG_REFERENCE="$recipe/kernel-build-reference.json"
export PONG_OUT="$PWD/out/pong-community-6.18.64"
export PONG_QEMU="$(command -v qemu-system-aarch64)"
bash devices/pong618/tools/build-release.sh
```

The source preflight checks the exact revisions and Android/stable ancestry,
so retain the source history. The build verifies all 209 vendor and 84 GKI
modules, symbol CRCs, module signatures and QEMU admission. It produces
`kernel-final`, `signed`, `frozen` and `release-report.json`.
Each builder generates a local module signing key. That public certificate is
embedded in the matching kernel.

The tested configuration uses Kleaf's unstamped `-maybe-dirty` suffix.
Both kernel and module checkouts were clean. An unstamped build does not
record its Git revision in `uname`; the manifest and qualification record
provide the exact revisions. A separately stamped build needs its own
qualification.

## Full Android source checkout

`full.xml` pins 1,260 Android and manually attached device projects, including
the audio MCS dependency. It uses public upstream bases for the three local
power-HAL, libperfmgr and update-engine adaptations. Their source deltas and
original commit metadata are in `patches/series.json`. The snapshot also
includes the existing SELinux mapping and two boot-control changes.

```sh
# Run in a new Android source directory, outside pong-build-support.
repo init -u https://github.com/DerpFest-AOSP/android_manifest.git -b 17
cp "$recipe/full.xml" .repo/manifests/pong618.xml
repo init -m pong618.xml
repo sync -c -j4

python3 "$recipe/apply-snapshot.py" --check
python3 "$recipe/apply-snapshot.py"
```

The patch tool checks each base revision, patch digest and before/after file
digest before applying changes. Running it again verifies an already-applied
snapshot. Local tests applied all six patch entries in isolated checkouts and
verified the result and the repeated check.

All Android projects have pinned Git revisions. A complete download and build
in a newly empty Android checkout remain unqualified. Repository access, Git
LFS dependencies and the usual Android build dependencies are required.

## Import the source-built kernel

Run the following in the Android source root. Set `kernel_workspace` to the
absolute path of the kernel workspace built above.

```sh
kernel_workspace=/absolute/path/to/pong-kernel-workspace
art="$kernel_workspace/out/pong-community-6.18.64"
bank="$PWD/device/nothing/Pong-kernel"
tools="$kernel_workspace/devices/pong618/tools"

python3 "$bank/import-source-build.py" --check-only \
  --kernel "$art/kernel-final" --signed "$art/signed" --frozen "$art/frozen" \
  --reference "$recipe/kernel-build-reference.json" --source-tools "$tools" \
  --destination "$bank" --lists "$bank"
python3 "$bank/import-source-build.py" \
  --kernel "$art/kernel-final" --signed "$art/signed" --frozen "$art/frozen" \
  --reference "$recipe/kernel-build-reference.json" --source-tools "$tools" \
  --destination "$bank" --lists "$bank"

export WITH_GMS=true TARGET_PONG_KERNEL=6.18
source build/envsetup.sh
lunch lineage_Pong-cp2a-user
m -j4 target-files-package
```

The prebuilt repository pinned by `full.xml` provides the tested DTB, DTBO and
startup lists. The import replaces its kernel and module cohort with the
fresh source build. It verifies every module and certificate before writing,
and requires the destination checkout to be clean. The imported bank has
293 modules and 100 first-stage modules.

Sign the target-files and OTA with maintainer-owned keys using
`device/nothing/Pong/tools/prepare-release-keys.py` and
`device/nothing/Pong/tools/sign-community.py`. The
[signing instructions](../community-clg43/README.md#kernel-sources-and-signing)
describe the key backup and signing process. Preserve existing vendor
PRESIGNED identities. Maintainer private keys are kept outside the repositories.
A self-built image signed with different keys needs a separately qualified
installation and data-migration procedure.

## Installed RC

The tested full OTA contains 13 signed partitions, including recovery.
All payload image digests and the AVB chain were verified. It was installed
using the existing recovery's standard sideload path. Android completed boot
on 6.18.64 with enforcing SELinux and verity. After PIN unlock, shared storage
was accessible and a pre-update file's SHA-256 still matched. Wi-Fi and mobile
networks were validated by Android.

The qualification applies to one 12 GB / 256 GB Nothing Phone (2). Physical
recovery rendering, early-boot display glitches, clean installation, long
untethered battery behavior and extended Bluetooth audio tests remain open.
The OTA's standalone `recovery.img` is byte-identical to the recovery in the
verified 16 November target-files. Its SHA-256 is
`d97b7b928bca5b8981118f180c0c212e81beb6c12440202503a7ceaf9cb3739b`.

Build, signing, OTA, and physical-feature evidence have separate scopes in
`qualification.json`.
