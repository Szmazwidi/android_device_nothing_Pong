# Experimental camera enumeration recovery

This optional component is disabled by default. Set
`PONG_EXPERIMENTAL_CAMERA_HEALTH := true` in the product configuration to
build it into a 6.18 ROM. It polls only public camera enumeration after boot
and requests at most one provider restart if fewer than two cameras appear.
It does not open cameras or save images.

The component and SELinux policy compiled successfully, but this automatic
restart path has not been tested on the device. It may interrupt an application
using the provider, and must not be enabled by default until its behavior and
interaction with active clients have been verified. A successful direct
camera probe on the current kernel is separate from testing this watchdog.
