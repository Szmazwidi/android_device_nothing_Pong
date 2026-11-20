# LHDCv5 test for Pong RC2

This optional change gives LHDCv5 a software output through Android's Bluetooth
audio HAL. SBC, AAC, aptX, aptX HD and LDAC retain the existing Qualcomm A2DP
routes. The patch changes Android Bluetooth and audio policy. The RC2 kernel,
module bank and recovery still apply.

The routing follows the separate LHDC output observed in Nothing OS
`Pong_B4.1-260618-1026`. The encoder and PCM path come from Android's Bluetooth
sources. The audio-policy profiles reuse the Android 7.0 Bluetooth policy
configuration. The patch retains the upstream files and their license notices.
[Nothing OS reference images](https://github.com/spike0en/nothing_archive/releases/tag/Pong_B4.1-260618-1026)

## Build

Prepare the pinned [RC2 source checkout](../../README.md#full-android-source-checkout)
and [kernel bank](../../README.md#import-the-source-built-kernel). Then run this
from the Android source root. `recipe` is the absolute path to the RC2 recipe
directory in the support checkout.

```sh
patch="$recipe/experiments/lhdcv5/LHDCv5-selective-RC2.patch"
git apply --check "$patch"
git apply "$patch"

export WITH_GMS=true TARGET_PONG_KERNEL=6.18
source build/envsetup.sh
lunch lineage_Pong-cp2a-user
m -j3 com.android.bt
m -j4 target-files-package
```

The Android source bases are `d50347ca16c270cec86a727de77b22c1156ff387` for the Pong
device tree, `2b3aafd7807d7e99606136e542936c325a7507bf` for DerpFest Bluetooth, and
`25c64ed45218ef124659047b441167051cb0cf5c` for the LineageOS SM8450 primary audio
HAL. See the [pinned manifest](../../full.xml) for the remaining projects.

## Test

The maintainer's experimental OTA is for the Nothing Phone (2) running the
Community RC2 signed with the same keys. Use the built-in updater's local update
option. See the [community signing guidance](../../../community-clg43/README.md#kernel-sources-and-signing)
for an image built with other keys.

Play a track with a compatible receiver and confirm LHDCv5 is the active codec.
Check playback with the screen off and after reconnecting. Then switch back to
AAC or LDAC and check that audio resumes. Include the receiver model and the
codec shown during playback when reporting the result.

[Host verification](qualification.json) covers the rebuilt Bluetooth module,
the declared audio routes, release signatures, and all 13 OTA partitions.
Playback, codec switching, and battery impact still need a hardware test.
