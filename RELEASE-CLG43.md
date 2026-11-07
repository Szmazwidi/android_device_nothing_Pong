# Community CLG43 release qualification

Build the device tree together with its pinned Pong-kernel community branch.
The bank contains 209 vendor modules and 84 GKI modules, with 100 first-stage
modules. WLAN options select DRV and cold boot calibration on one cnss2 line.
The device source loads the fingerprint, memory, DSP, sensor, audio and camera
providers through native init services.

## Update and signing

Use a matching recovery, an unlocked bootloader and the firmware version
actually qualified for the target hardware. The payload contains recovery and
vbmeta partitions as well as the Android images. A component-only kernel test
and a complete ROM installation have different recovery requirements.

Maintain APK/APEX, OTA and AVB release identities outside source control.
Changing a system package's certificate requires a qualified migration for
existing data and shared UID state. A new release certificate alone does not
establish data-preserving upgrade compatibility from a test-key installation.

The development phone contains personal data. Its qualification path preserves
userdata and metadata. Fresh installation and other RAM/UFS variants require
separate test environments before a universal hardware claim can be made.

## Feature coverage

Record first and second boot, encryption/checkpoint, physical display and
fingerprint, RAM/CPU/thermal, microphones and audio routes, camera capture and
encoding, cellular data/IMS/calls/SMS, Wi-Fi/BT, GNSS, NFC with a tag, charging
and a complete untethered suspend/wake/USB cycle. Mark unperformed physical
tests explicitly. The OTG/FSA development branches are separate from CLG43.

Historical image reports and preserved failures remain in the source history.
