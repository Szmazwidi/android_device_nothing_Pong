# Pong Android 17 / Linux 6.18.64 RC

This directory records the source recipe for the signed DerpFest RC2 OTA
tested on 18 November 2026. The kernel is Linux 6.18.64 with the retained
Android 17 ACK and Pong adaptations. RC2 rebuilds Android from the pinned
sources and includes the power-off charger initialization fix.

The tested kernel revision is
`febb385ea217722658e25cebffc2e79171be69c7`. The matching module revision is
`bc31a11678ace6bd8a2af7f33cf49278a169e201`. The functional device-tree
revision is `d50347ca16c270cec86a727de77b22c1156ff387`.
[RC2 qualification](qualification-rc2.json) records the host and device results.
[RC1 qualification](qualification.json) records the earlier OTA.
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

`full.xml` pins 1,261 Android and device projects, including audio MCS and the
Pong-Development 5.10 module tree used to export Qualcomm display and audio
headers for Android. The 6.18 kernel build supplies the installed modules.
The recipe uses public upstream bases for the three local
power-HAL, libperfmgr and update-engine adaptations. Their source deltas and
original commit metadata are in `patches/series.json`. The snapshot also
includes the existing SELinux mapping and two boot-control changes.

```sh
# Run in a new Android source directory, outside pong-build-support.
repo init --git-lfs -u https://github.com/DerpFest-AOSP/android_manifest.git -b 17
cp "$recipe/full.xml" .repo/manifests/pong618.xml
repo init --git-lfs -m pong618.xml
repo sync -c -j4

for project in vendor/nothing/Pong vendor/pixel/gms; do
  (
    set -o pipefail
    cd "$project" || exit 1
    git lfs ls-files --long HEAD | sed -E 's/^([0-9a-f]{64}) [*-] /\1  /' | sha256sum --strict --check --quiet
  ) || exit 1
done

python3 "$recipe/apply-snapshot.py" --check
python3 "$recipe/apply-snapshot.py"
```

The patch tool checks each base revision, patch digest and before/after file
digest before applying changes. Running it again verifies an already-applied
snapshot. Local tests applied all six patch entries in isolated checkouts and
verified the result and the repeated check.

The RC2 checkout used an existing tree as a Git object cache and a separate
output directory. Compiling the display HAL exposed the missing header
dependency. After adding it, both display objects compiled and the full
target-files build completed in the same output directory. The vendor and
GMS LFS files matched their pinned digests. A full uncached download has
yet to be tested.

## Import the source-built kernel

Run the following in the Android source root. Set `kernel_workspace` to the
absolute path of the kernel workspace built above.

```sh
kernel_workspace=/absolute/path/to/pong-kernel-workspace
art="$kernel_workspace/out/pong-community-6.18.64"
bank="$PWD/device/nothing/Pong-kernel"
tools="$kernel_workspace/devices/pong618/tools"
lists=$(mktemp -d)
for name in modules.load modules.load.vendor_boot modules.list.vendor_boot; do
  git -C "$bank" show "HEAD:$name" > "$lists/$name" || exit 1
done

python3 "$bank/import-source-build.py" --check-only \
  --kernel "$art/kernel-final" --signed "$art/signed" --frozen "$art/frozen" \
  --reference "$recipe/kernel-build-reference.json" --source-tools "$tools" \
  --destination "$bank" --lists "$lists"
python3 "$bank/import-source-build.py" \
  --kernel "$art/kernel-final" --signed "$art/signed" --frozen "$art/frozen" \
  --reference "$recipe/kernel-build-reference.json" --source-tools "$tools" \
  --destination "$bank" --lists "$lists"

export WITH_GMS=true TARGET_PONG_KERNEL=6.18
export BUILD_DATETIME=$(date +%s)
export BUILD_NUMBER="$BUILD_DATETIME"
source build/envsetup.sh
lunch lineage_Pong-cp2a-user
m -j4 target-files-package
```

Keep this checkout and its `out` directory for subsequent edits. Running the
same target reuses completed compilation steps. An empty output directory is
useful for checking the published recipe independently.

The prebuilt repository pinned by `full.xml` provides the tested DTB, DTBO and
startup lists. The import replaces its kernel and module cohort with the
fresh source build. It verifies every module and certificate before writing,
and requires the destination checkout to be clean. The imported bank has
293 modules and 100 first-stage modules.

Sign the target-files and OTA with maintainer-owned keys using the tools in
the support checkout, which includes the OTA identity guard. Pass
`--previous-ota /path/to/last-trusted-Pong.zip` to
`sign-community.py` on every update. The build timestamp and numeric
incremental must both increase. Set a fresh build date and number before
building Android; editing ZIP metadata does not change the installed
properties. Use `--first-release` only for a new signing track. To check
an already packaged OTA, including one produced by an alternate packager,
run `python3 "$recipe/../../tools/ota_identity.py" previous.zip candidate.zip`.
The [signing instructions](../community-clg43/README.md#kernel-sources-and-signing)
describe the key backup and signing process. Preserve existing vendor
PRESIGNED identities. Maintainer private keys are kept outside the repositories.
A self-built image signed with different keys needs a separately qualified
installation and data-migration procedure.

## Installed RC2

The signed full OTA covers 13 partitions, including recovery. The payload
image digests, package signature and AVB chain passed verification. Android
booted on the alternate slot after recovery sideload. Shared storage remained
accessible after PIN unlock and Android validated Wi-Fi and mobile data.

After a full shutdown, connecting a charger displayed the battery percentage.
The phone then booted the same signed RC2 image and reached the Wi-Fi gateway
with Bluetooth enabled.

The test covered one 12 GB / 256 GB Nothing Phone (2). Cold Wi-Fi reconnect
with Bluetooth and BLE scanning disabled, physical recovery rendering,
early-boot display glitches, clean installation, long battery tests and
extended Bluetooth audio remain open.
