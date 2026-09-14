# Nothing Phone (2) — Pong

Device configuration for the **Nothing Phone (2)** (`Pong`) targeting **Android 17 / LineageOS 24.0**.

> **Status:** community / development bring-up<br>
> **Branch:** `lineage-24.0`<br>
> **Android:** 17<br>
> **Device:** Nothing Phone (2)<br>
> **Codename:** `Pong`

This is not an official LineageOS-supported device tree.

## Repositories

The following nine Pong-specific projects were verified against the local checkout,
`.repo/local_manifests/pong.xml`, the resolved manifest and public branch tips on
2026-09-14. The three maintained forks use `lineage-24.0`.

| Checkout path | Repository | Tracking branch |
| --- | --- | --- |
| `device/nothing/Pong` | [Szmazwidi/android_device_nothing_Pong](https://github.com/Szmazwidi/android_device_nothing_Pong) | `lineage-24.0` |
| `vendor/nothing/Pong` | [Szmazwidi/android_vendor_nothing_Pong](https://github.com/Szmazwidi/android_vendor_nothing_Pong) | `lineage-24.0` |
| `kernel/nothing/sm8475` | [Szmazwidi/android_kernel_nothing_sm8475](https://github.com/Szmazwidi/android_kernel_nothing_sm8475) | `lineage-24.0` |
| `kernel/nothing/sm8475-modules` | [Pong-Development/kernel_nothing_sm8475-modules](https://github.com/Pong-Development/kernel_nothing_sm8475-modules) | `test` |
| `kernel/nothing/sm8475-devicetrees` | [Nothing-phone-2-Development/android_kernel_nothing_sm8475-devicetrees](https://github.com/Nothing-phone-2-Development/android_kernel_nothing_sm8475-devicetrees) | `lineage-23.0` |
| `hardware/dolby` | [Pong-Development/hardware_dolby](https://github.com/Pong-Development/hardware_dolby) | `16` |
| `hardware/qcom-caf/sm8450/display` | [Pong-Development/hardware_qcom-caf_sm8450_display](https://github.com/Pong-Development/hardware_qcom-caf_sm8450_display) | `16.2` |
| `packages/apps/GlyphAdapter` | [Pong-Development/packages_apps_GlyphAdapter](https://github.com/Pong-Development/packages_apps_GlyphAdapter) | `16` |
| `packages/apps/ParanoidGlyphPhone2` | [Pong-Development/packages_apps_ParanoidGlyph](https://github.com/Pong-Development/packages_apps_ParanoidGlyph) | `17` |

The base manifest is `LineageOS/android`, branch `lineage-24.0`; the audited
manifest commit is `ad6b6d6bfc16cb0cd3c39db18685a72a6a43985a`.
It supplies the remaining platform dependencies, including Qualcomm common/audio,
Google interfaces and power libraries, Lineage interfaces, vendor Qualcomm sources,
SEPolicy and the `clang-r563880c` toolchain. Do not replace them with guessed device forks.

The display project replaces `hardware/qcom-caf/sm8450/display` from the base
manifest. Install only one Pong local manifest at a time.

| Manifest | Purpose |
| --- | --- |
| [pong-a17.xml](manifests/pong-a17.xml) | Tracks the verified branches; platform and dependencies may advance. |
| [pong-a17-known-good.xml](manifests/pong-a17-known-good.xml) | Pins nine Pong project commits only; the base platform still floats. |
| [pong-a17-full-known-good.xml](manifests/pong-a17-full-known-good.xml) | Full resolved snapshot of 1,245 projects, used with the captured local patches below. |

**The nine-project overlay alone does not reproduce the working tree.** The audit
found uncommitted changes in 13 projects (101 files), including required platform
build fixes and a missing comma in Dolby. These are included in
[the snapshot patch bundle](manifests/patches/series.json), with original revisions
and before/after SHA-256 checksums. See [snapshot notes](manifests/README.md).

## Android 17 changes

### Fingerprint

The Android 17 branch switches the fingerprint implementation to the **HIDL 2.3 fingerprint HAL**.

The previously used custom AIDL wrapper consistently failed during Goodix UDFPS enrollment in secure preprocessing:

```text
[GF_HAL][CaEntry]: [sendCommand] QSEE TEE execute command failed.
[GF_HAL][ShenzhenAlgo]: [enrollImage] exit. err=GF_ERROR_PREPROCESS_FAILED, errno=1011
```

Using the HIDL 2.3 service on Android 17:

- fingerprint enrollment completes successfully;
- fingerprint authentication works;
- the existing Goodix TA, calibration and persist data can operate successfully.

The active service is:

```text
android.hardware.biometrics.fingerprint@2.3-service.nt.pong
```

This strongly points to the tested AIDL integration/wrapper path as the source of the enrollment failure rather than the fingerprint sensor, Goodix TA, calibration data or optical hardware path.

### Wireless Display

Android 17 compatibility patches are included for the proprietary WFD stack.

They currently include:

- adding `libinput_shim.so` to `libwfdnative.so`;
- removing the obsolete `android.hidl.base@1.0.so` dependency;
- removing the obsolete `libheif.so` dependency from `libwfdcommonutils.so`;
- allowing `lseek` in the `tcmd` seccomp policy.

The corresponding blob changes are reproduced through device-side blob fixups rather than relying only on manually patched proprietary binaries.

These are compatibility fixes for the WFD stack; they should not be interpreted as a claim that every Android 17 desktop-mode or external-display path is fully supported.

### QCA6490 Wi-Fi / Bluetooth power sequencing

The Android 17 kernel branch contains a Pong-specific fix for QCA6490 shared PMU power sequencing.

On the affected startup path, the WLAN PCIe endpoint may fail to respond when `WLAN_EN` is asserted while `BT_EN` remains low.

The fix:

1. temporarily asserts `BT_EN` when necessary during WLAN power-up;
2. allows the shared PMU/AON path to initialize;
3. asserts `WLAN_EN`;
4. releases the temporary `BT_EN` assertion after WLAN probe;
5. preserves `BT_EN` when Bluetooth is actually powered.

The implementation exposes Bluetooth power state to CNSS2 so temporary bootstrap ownership can be released safely.

The public patch passes `checkpatch.pl` with:

```text
0 errors, 0 warnings
```

The cleaned Android 17 source tree was also successfully built after applying the final kernel patch.

## Other device-tree changes

The `lineage-24.0` branch also contains Android 17 bring-up adjustments including:

- fingerprint HAL migration to HIDL 2.3;
- shipping API level aligned with the Nothing Phone (2) launch API level (`33`);
- Android 17-compatible SELinux Treble labeling configuration;
- separate normal and recovery init modules;
- updated UDFPS enrollment progress geometry;
- Android 17 WFD blob compatibility fixups.

## Building

### Host preparation

Use an x86-64 Linux host, a case-sensitive filesystem, Bash, Git, Git LFS, Python 3
and the Google `repo` launcher. Follow the official
[Android host setup](https://source.android.com/docs/setup/start/initializing) and
[hardware requirements](https://source.android.com/docs/setup/start/requirements).
The audited build host uses CachyOS; distro-specific package names differ.
Install your distro's Android build dependencies before syncing. The tree includes
its Java and Clang prebuilts; do not substitute a host compiler for the pinned kernel compiler.

For Ubuntu, the AOSP host package list plus the tools used in this guide is:

```bash
sudo apt-get update
sudo apt-get install git-core gnupg flex bison build-essential zip curl \
  zlib1g-dev libc6-dev-i386 x11proto-core-dev libx11-dev lib32z1-dev \
  libgl1-mesa-dev libxml2-utils xsltproc unzip fontconfig \
  git-lfs python3 repo
```

AOSP currently recommends at least 400 GB free disk space and 64 GB RAM.
Allow additional space for retained outputs and caches. These are upstream host
recommendations, not a measured minimum for Pong.

Check the tools before continuing:

```bash
git --version
git lfs version
python3 --version
repo version
```

### Recommended: reproduce the captured source state

Use a **new, empty source directory**. Keep the support checkout next to it:
the pinned device commit predates these instructions and does not contain the new
manifest/patch files. The separate checkout prevents them disappearing during sync.

```bash
mkdir -p pong-build
cd pong-build
git clone --branch lineage-24.0 --single-branch \
  https://github.com/Szmazwidi/android_device_nothing_Pong.git pong-build-support
# Record this commit alongside build artifacts; it identifies this manifest/patch bundle.
git -C pong-build-support rev-parse HEAD
mkdir android17
cd android17
repo init -u "$(cd ../pong-build-support && pwd)" -b lineage-24.0 \
  -m manifests/pong-a17-full-known-good.xml --git-lfs --no-clone-bundle
repo sync -c -j4 --fail-fast
```

This full manifest is standalone: **do not add any Pong local manifest** to it.
All fetch URLs are absolute public URLs. Avoid shallow history for the snapshot:
some pinned revisions are older than the latest branch tip.

Download LFS objects for every project that uses them, then verify the vendor blobs:

```bash
repo forall -c '
  lfs_files=$(git lfs ls-files) || exit 1
  if [ -n "$lfs_files" ]; then
    git lfs pull && git lfs fsck || exit 1
  fi
'
git -C vendor/nothing/Pong lfs ls-files
git -C vendor/nothing/Pong lfs fsck
```

The vendor repository contains six LFS-managed camera libraries. Entries in
`git lfs ls-files` must have `*` (materialized content), not `-` (pointer files).
A successful Git checkout with unresolved LFS pointers is insufficient for building.
Do not set `GIT_LFS_SKIP_SMUDGE=1` unless you subsequently fetch and check out the objects.

Apply the captured local changes before selecting the target:

```bash
python3 ../pong-build-support/manifests/apply-snapshot.py --check
python3 ../pong-build-support/manifests/apply-snapshot.py
```

The helper checks all affected project HEADs, patch checksums and file contents
before writing. It accepts an already fully applied bundle and refuses unexpected
or partly applied changes. It does not commit changes. Keep these patches after
sync; they are part of this source snapshot.

### Select the product and build

From the Android source root, after syncing and applying the snapshot patches:

```bash
source build/envsetup.sh
lunch lineage_Pong cp2a userdebug
m bacon
```

`source build/envsetup.sh` runs the device's `vendorsetup.sh`, which reconstructs
`vendor/nothing/Pong/proprietary/vendor/lib64/libhyperzoom.arcsoft.so` from the
tracked `.part*` files. Do not bypass this step. The legacy lunch syntax
`lunch lineage_Pong-cp2a-userdebug` is also supported by the audited build system.

Outputs are under `out/target/product/Pong/`, including the LineageOS ZIP.
Development image targets are `m bootimage vendorbootimage dtboimage`.
Save the build log, support checkout commit, resolved manifest and patch bundle
with your outputs. A manifest records commits, not uncommitted patches:

```bash
repo manifest -r -o out/pong-build-resolved.xml
repo status > out/pong-build-status.txt
```

The snapshot captures the audited source state; it is not a claim of byte-identical
ZIP reproduction. Timestamps, signing keys, host environment and build options
also affect outputs. This packaging has not yet been tested by a new full clean build.

### Tracking branches for development

For a separate fresh checkout that follows upstream updates:

```bash
mkdir android17-current
cd android17-current
repo init -u https://github.com/LineageOS/android.git -b lineage-24.0 \
  --git-lfs --no-clone-bundle
mkdir -p .repo/local_manifests
curl --fail --location \
  https://raw.githubusercontent.com/Szmazwidi/android_device_nothing_Pong/lineage-24.0/manifests/pong-a17.xml \
  -o .repo/local_manifests/pong.xml
repo sync -c -j4 --fail-fast
```

Run the LFS steps above. This mode is for development, and is not the known-good
source recipe. The platform fixes captured above may need rebasing as branches
advance; the snapshot helper deliberately refuses different project revisions.
The nine-project pinned overlay can be used instead by downloading
`pong-a17-known-good.xml` into the same `.repo/local_manifests/pong.xml` filename,
but it still does not pin the platform or replace the full snapshot procedure.

For an existing checkout, review `.repo/local_manifests/` before migration. Do not
install these alongside an older `pong.xml` or a generated `roomservice.xml` that
already declares these paths. Preserve local changes; use a fresh directory when
switching between this snapshot and tracking branches. Do not use `--force-sync`
as a routine fix for duplicate projects or changed remotes.

## Firmware and proprietary files

This tree relies on proprietary Nothing, Qualcomm and Goodix components.

The associated vendor repository contains the proprietary files used by the current Android 17 bring-up.

A precise minimum stock firmware requirement is not documented here yet. Use a firmware/vendor base compatible with the proprietary files referenced by the current tree.

## Known notes and limitations

This is a community Android 17 bring-up and should not be treated as an official LineageOS release.

The fingerprint implementation intentionally uses HIDL 2.3 because the tested custom AIDL implementation fails Goodix enrollment during secure preprocessing on Android 17.

Further runtime testing may reveal issues outside the functionality tested during the current bring-up.

## AI-assisted development

Parts of the Android 17 bring-up and some of the patches in this repository were developed with assistance from **OpenAI's ChatGPT (GPT-5.6 Sol)**.

AI assistance was used as an engineering tool for:

- source-code analysis;
- log analysis;
- debugging;
- comparing implementation paths;
- patch review;
- suggesting and refining code changes.

Changes were **not accepted or published blindly**.

The maintainer reviewed the resulting modifications, built the source and, where applicable, tested the relevant behavior on actual Nothing Phone (2) hardware.

Debugging conclusions were additionally checked against available source code, runtime logs, binary behavior, hashes, build results and controlled A/B tests where practical.

> **AI-assisted, human-reviewed, build-tested, and hardware-tested where applicable.**

LLM assistance is treated here as another engineering and debugging tool, not as a substitute for technical review or validation.

## Upstream and credits

This work builds on the existing Nothing Phone (2) development trees and the work of their maintainers and contributors.

Credits include:

- Pong-Development
- LineageOS
- Nothing Phone (2) device developers and contributors
- Android and Linux kernel contributors

The repositories under `Szmazwidi` are maintained as GitHub forks of their respective Pong-Development repositories so that upstream history and attribution remain intact.

## Contributions and bug reports

Technical review, bug reports and patches are welcome.

Useful bug reports should include, where applicable:

- exact source revision / commit;
- Android build version;
- relevant `logcat`;
- relevant kernel logs;
- clear reproduction steps.

Please avoid reporting an issue solely because LLM assistance was used during development. Reproducible failures, technical criticism, code review and better implementations are welcome.
