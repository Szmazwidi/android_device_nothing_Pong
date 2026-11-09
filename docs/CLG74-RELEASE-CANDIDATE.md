# CLG74 — Nothing Phone (2) (Pong) community release candidate

**Status (2026-11-09): public candidate links supplied by the maintainer; installation reported on one phone; stable release qualification is still open.**

This document distinguishes the CLG74 **LAB** validation cohort from the two public download links supplied by the maintainer. The maintainer reports both ROM and matching recovery installed on their Nothing Phone (2) on 2026-11-09. This statement is a **maintainer report, not a new independent kernel/Android boot, partition-integrity or signed-image verification**. The contents and SHA-256 hashes of the exact MEGA downloads have not been independently retrieved or checked here. **This is not an installation guide or a stable-release qualification.**

## Identity and scope

- Device: Nothing Phone (2), codename `Pong`.
- Android: 17 (community / unofficial ROM bring-up).
- Kernel tested on hardware: **Linux 6.18.60, 4 KiB pages**.
- Validation phone: **one EEA device, nominal 12 GB RAM / 256 GB UFS**. Other hardware variants are not qualified.
- Tests listed below were performed against a signed **CLG74 LAB** image set on a physical phone with SELinux **Enforcing**, **not** against a newly installed public/community OTA.
- The matching kernel image was observed with `CONFIG_MODULE_SIG_FORCE=y`; the tested LAB AVB digest matched its signed image set.

## Candidate downloads (maintainer-provided, verification pending)

- **ROM:** [MEGA — ROM for Pong](https://mega.nz/file/K5JA0ZoR#ZQXql1Ip_F56TuuBVAo3g50qHw-MKkGXd03KJNniiI4)
- **Recovery:** [MEGA — recovery for Pong](https://mega.nz/file/voIwwRSI#V2zhfOYhegMfz6lEGK6khH0OWPdDPIIXaM0xegnKSlM)

**Reported device action:** the maintainer says the complete ROM and recovery have been flashed to the test phone. No post-flash `sys.boot_completed=1`, partition SHA-256 readback, recovery boot test, OTA installation journal or first-boot qualification for the **exact files above** was provided with this update. Therefore the links are listed for identification and review, **not as a verified stable or safe dirty-flash package**. File names, sizes, independently computed SHA-256, signed build identity and firmware requirements remain unverified. The MEGA web endpoint could not be read by the verification environment.

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

1. **Package identity:** independently obtain and verify the supplied community ROM and recovery images, full ZIP and payload signatures, AVB, module signatures, public SHA-256, exact Android build identity and matching CLG74 source revisions. Do not conflate prior signed test artifacts with these downloads.
2. **Recovery and installation:** although the maintainer reports that ROM and recovery are now installed on one phone, still collect evidence of actual boot completion, installed partition identities and recovery functionality, then qualify clean installation, complete OTA partition set, cold boot, and (if explicitly offered) data-preserving update from an identified previous signing identity. Keep backups and independently checked restore images.
3. **Connectivity on the installed release:** Wi-Fi join and Internet traffic; cellular data, SMS and voice calls; Bluetooth pairing and audio; physical NFC tag; GNSS.
4. **Everyday device functions:** fingerprint enrollment/unlock, display and touch, cameras (still/video and normal applications), microphones, audio routes, charging and thermal behavior.
5. **Power and storage:** untethered repeated suspend/resume, overnight standby drain and repeat sequential-read measurement.
6. **Compatibility:** verify firmware baseline, encryption/FBE and additional RAM/UFS variants before making universal device claims.

Successful prior CLG43 or CLG72 tests are **historical references**, not replacements for testing the exact CLG74 community package.

## User-facing safety information

- **Do not treat this candidate as a qualified stable release.** Do not install an internal LAB image as a community release.
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
- Independently confirmed ROM and recovery filenames, sizes and SHA-256 (the download URLs are now available).
- Final source commits and source manifest.
- GApps inclusion and root / KernelSU status of the public build.
- Verified package-specific recovery, firmware and installation / update procedure.
- Final release classification (testing / beta / stable) after hardware qualification.

No phone operations, flash, reset or signing-key changes are authorized or performed by publishing this note.
