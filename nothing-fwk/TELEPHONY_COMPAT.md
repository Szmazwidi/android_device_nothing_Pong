# Nothing telephony compatibility shim

The Qualcomm qcrilmsgtunnel APK references `INothingTelephony.Stub.asInterface`
and `generalSetter`. Without these classes it can crash while handling RRC
notifications. This package includes the unchanged Apache-2.0 compatibility
stub authored by Mashopy in
[CMF-Phone-1 commit cc2efe1cce13](https://github.com/CMF-Phone-1/android_device_nothing_Tetris/commit/cc2efe1cce13cae3d18951870e347ee20357429c).
It is compiled into the existing `nothing-fwk` boot jar; the upstream path is
adapted to this device tree's `nothing-fwk/src` layout.

The stub returns null for an absent or non-local service. It does **not**
implement an OEM Binder proxy, deliver Nothing radio notifications, or replace
testing mobile data, calls or IMS. The development phone did not expose
`nothing.radio.ntphone` when this was prepared. Null and local-interface
behavior were tested on a host; loading the class, the null path and referenced
method signature were tested in an isolated Android ART process. Integration
into the ROM and elimination of the real service crash are not yet verified.
