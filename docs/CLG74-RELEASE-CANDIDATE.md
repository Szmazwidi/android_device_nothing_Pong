# CLG74 — Nothing Phone (2) (Pong) community release candidate

**Status (2026-11-09): pre-release qualification; NOT a stable or approved public installation.**

This document records what has actually been demonstrated for the CLG74 **LAB** cohort and what still needs to be tested for a separately signed **community** package. It is **not an installation guide**. No public ZIP, SHA-256 checksum, recovery image or installation commands should be inferred from it.

## Identity and scope

- Device: Nothing Phone (2), codename `Pong`.
- Android: 17 (community / unofficial ROM bring-up).
- Kernel tested on hardware: **Linux 6.18.60, 4 KiB pages**.
- Validation phone: **one EEA device, nominal 12 GB RAM / 256 GB UFS**. Other hardware variants are not qualified.
- Tests listed below were performed against a signed **CLG74 LAB** image set on a physical phone with SELinux **Enforcing**, **not** against a newly installed public/community OTA.
- The matching kernel image was observed with `CONFIG_MODULE_SIG_FORCE=y`; the tested LAB AVB digest matched its signed image set.

## Observed hardware results for CLG74 LAB

- Android booted on the physical device with Linux 6.18.60.
- Four microphone recording modes passed.
- Rear and front camera recording, with audio, passed at 640×480 and 1080p in the diagnostic application.
- A Wi-Fi scan detected **28 access points**. This is **not** a Wi-Fi association, authentication or Internet traffic test.
- The inspected boot-to-test kernel log had **zero observed kernel panics, Oops and UFS/filesystem errors**, and the inspected Android log had **no matched FATAL or ANR**. This is bounded log evidence, **not** a guarantee of stability.
- The prior `queue_work_on` SLIMbus warning and wakeup-statistics read denials were not observed in this CLG74 boot. Other SLIMbus, FastRPC CMA, camera HAL and tethering messages remain for investigation.
- The local benchmark recorded **293 samples with zero measurement errors**. An unrelated cleanup assertion left a benchmark scratch directory.
- Random-read QD32 was approximately **126k IOPS**. Sequential read measured approximately **14% below CLG72 in one sample per build**; repeatability has not been established.
- **Untethered suspend / overnight drain has not been measured on CLG74.** A previous approximately 7.4 mA overnight result belongs to CLG72 and cannot be represented as a CLG74 result.

## Required gates before a release is labeled stable

1. **Package identity:** finish community target-files build and signing; independently verify the finished OTA ZIP, payload, AVB, module signatures, public SHA-256 and provenance against the exact CLG74 source revisions.
2. **Recovery and installation:** perform an authorized, reversible preflight with backups and checked restore images. Qualify a clean installation, matching recovery, complete OTA partition set, cold boot, and (if explicitly offered) data-preserving update from an identified previous signing identity.
3. **Connectivity on the installed release:** Wi-Fi join and Internet traffic; cellular data, SMS and voice calls; Bluetooth pairing and audio; physical NFC tag; GNSS.
4. **Everyday device functions:** fingerprint enrollment/unlock, display and touch, cameras (still/video and normal applications), microphones, audio routes, charging and thermal behavior.
5. **Power and storage:** untethered repeated suspend/resume, overnight standby drain and repeat sequential-read measurement.
6. **Compatibility:** verify firmware baseline, encryption/FBE and additional RAM/UFS variants before making universal device claims.

Successful prior CLG43 or CLG72 tests are **historical references**, not replacements for testing the exact CLG74 community package.

## User-facing safety information

- **Do not install a LAB image as a community release.**
- **Do not relock the bootloader** with a custom-key community build; this path is not qualified.
- No minimum stock firmware version has been established. Do not substitute a guessed version.
- **Do not assume a dirty flash is safe.** APK/APEX/shared-UID and OTA signing-key migration must be explicitly qualified. Likewise, a clean install may erase `/data`; a slot change does not restore shared data.
- Do not flash `recovery`, `vbmeta` or overwrite dynamic `super` partitions based solely on this document. Wait for a verified package-specific installation procedure.

## Source and build provenance

- [Device sources and community source recipe](https://github.com/Szmazwidi/android_device_nothing_Pong/tree/pong-6.18-community-clg43)
- [CLG43 community build procedure](https://github.com/Szmazwidi/android_device_nothing_Pong/blob/pong-6.18-community-clg43/manifests/community-clg43/README.md)
- [Existing release-qualification requirements](https://github.com/Szmazwidi/android_device_nothing_Pong/blob/pong-6.18/RELEASE-CLG43.md)

**Important:** those links currently describe the older **CLG43** source cohort. They must **not** be presented as proof that the exact **CLG74** candidate can be reproduced. Publish CLG74 kernel/modules/device/prebuilt source revisions and the final matching manifest before advertising a CLG74 source download.

## Pending publication fields

The following must be supplied from the final signed artifact (not guessed):

- Exact ROM branding, build identifier and security patch level.
- Community OTA filename, size and SHA-256.
- Final source commits and source manifest.
- GApps inclusion and root / KernelSU status of the public build.
- Verified package-specific recovery, firmware and installation / update procedure.
- Final release classification (testing / beta / stable) after hardware qualification.

No phone operations, flash, reset or signing-key changes are authorized or performed by publishing this note.
