# Nothing Phone (2) — Pong

Device configuration for the **Nothing Phone (2)** (`Pong`) targeting **Android 17 / LineageOS 24.0**.

> **Status:** community / development bring-up<br>
> **Branch:** `lineage-24.0`<br>
> **Android:** 17<br>
> **Device:** Nothing Phone (2)<br>
> **Codename:** `Pong`

This is not an official LineageOS-supported device tree.

## Repositories

The Android 17 bring-up currently uses the following maintained forks:

| Component | Repository | Branch |
| --- | --- | --- |
| Device | `Szmazwidi/android_device_nothing_Pong` | `lineage-24.0` |
| Vendor | `Szmazwidi/android_vendor_nothing_Pong` | `lineage-24.0` |
| Kernel | `Szmazwidi/android_kernel_nothing_sm8475` | `lineage-24.0` |

Kernel modules and kernel devicetrees currently remain based on their existing upstream repositories because no local Android 17-specific changes were required there.

The source tree also uses existing Pong development repositories for components such as:

- kernel modules
- kernel devicetrees
- Dolby hardware support
- Qualcomm SM8450 display HAL
- GlyphAdapter
- ParanoidGlyphPhone2

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

A complete compatible Android / LineageOS source tree is required.

The current Android 17 configuration uses:

- product: `lineage_Pong`
- release: `cp2a`
- variant: `userdebug`

Initialize the build environment:

```bash
source build/envsetup.sh
lunch lineage_Pong cp2a userdebug
```

The legacy combined syntax is also accepted by the current build system:

```bash
lunch lineage_Pong-cp2a-userdebug
```

Build the ROM with:

```bash
m bacon
```

Individual images can also be built during development, for example:

```bash
m bootimage vendorbootimage dtboimage
```

Before building, make sure all required Pong vendor, kernel, kernel modules, kernel devicetrees and hardware repositories are present at compatible revisions.

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
