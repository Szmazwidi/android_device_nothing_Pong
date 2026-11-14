# Pong 6.18.63 WLAN and FastRPC source candidate

This recipe builds the kernel and 293 modules for Nothing Phone (2) / Pong.
The manifest pins the kernel and module commits along with the Android Kleaf
toolchain. The build includes the 6.18.63 compatibility and IR fixes, the VIDC
control query fix, FastRPC ADSP/SLPI restart registration and the closed-WLAN
suspend fix.

## Build from sources

Use a Linux host with the Android kernel build dependencies, `repo` and
`qemu-system-aarch64`. Keep the device-tree checkout outside the Kleaf workspace.

```sh
git clone --single-branch --branch pong-6.18-community-wlan-fastrpc \
  https://github.com/Szmazwidi/android_device_nothing_Pong.git pong-device
recipe="$(realpath pong-device/manifests/community-6.18.63-wlan-fastrpc)"
mkdir pong-kernel-workspace && cd pong-kernel-workspace
repo init -u https://android.googlesource.com/kernel/manifest -b common-android17-6.18
cp "$recipe/kernel.xml" .repo/manifests/pong618.xml
repo init -m pong618.xml
repo sync -c -j4
PONG_REFERENCE="$recipe/kernel-build-reference.json" \
PONG_OUT="$PWD/out/pong-community" \
bash devices/pong618/tools/build-release.sh
```

The preflight checks the kernel and module ancestry, so keep the history of
those projects available. The build generates and uses a local module signing
key. Use `kernel-final`, `signed` and `frozen` from the output directory to
build the matching device prebuilts with `Pong-kernel/import-source-build.py`.
Start with the device configuration in this branch and the existing
[Android build instructions](../community-clg43/README.md) for the overall
checkout and packaging process. Use this directory's kernel recipe for the
kernel and module bank.

For a DerpFest Android tree at update_engine base
`23d98b79f652ffb5cc1c1c4fb080c579ee2dbe45`, apply
[the updater patch](update-engine-restore-verification.patch) in that
project with `git am`. It restores payload signature and downgrade checks.
The patch retains its original commit metadata and revert reference.

## Qualification

- The exact combined kernel and module sources passed the pinned Kleaf
  build, ABI and signature checks for all 293 modules, and the QEMU module
  admission test. [Host validation](host-validation.json).
- The WLAN and FastRPC changes were built separately with Kleaf. Each was
  tested on the signed 6.18.63 base. FastRPC registered ADSP and SLPI and opened
  both RPMsg channels. The WLAN test booted Android with enforcing
  SELinux/verity and rejoined a saved network. Its untethered idle drain and
  recovery after a WLAN HAL failure still need measurement.
- A full OTA using this exact combined build still needs packaging and
  on-device qualification. This is a source candidate for development.
