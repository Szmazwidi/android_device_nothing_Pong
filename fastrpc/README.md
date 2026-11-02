# Native CDSP FastRPC for the 6.18 kernel profile

Upstream: https://github.com/qualcomm/fastrpc, tag v1.0.8,
commit d247519650fe5cb16de6c78edaa95bcc4be25073. The upstream subtree was
imported without squashing, retaining original authors, history and license
notices. This is integration of Qualcomm's implementation, not new authorship
of its RPC stack. See upstream/LICENSE.txt and per-file notices.

Only TARGET_PONG_KERNEL=6.18 selects pong_cdsprpcd, providing a separate
pong-cdsprpcd executable. Its init override retains the vendor.cdsprpcd service
identity, UID/groups, domain and existing disable property. The original binary
remains installed for the other kernel profiles. ADSP/audio and SDSP/sensor proprietary clients remain selected.
The two new library names isolate this stack from existing libadsprpc/libcdsprpc
consumers. The native CDSP kernel binding used by EVA is preserved.

The local upstream-source change makes DMA_HEAP_NAME configurable. The build
selects /dev/dma_heap/qcom,system because the selected Qualcomm FastRPC driver
requires mem_buf VM ownership metadata, absent from the generic system heap.
No ownership, signature or permission check is removed. Native CDSP nodes use
the existing vendor_qdsp_device/vendor_xdsp_device labels; no new allow rule is
introduced. Enforcing remains required.

The legacy daemon was traced issuing its initialization ioctl to
/dev/adsprpc-smd-secure and receiving ENODEV repeatedly. The Android/Soong-built
replacement booted on the development handset under vendor_cdsprpcd with SELinux
Enforcing. Its open descriptors confirm the native CDSP endpoint and Qualcomm
heap; the default listener established without that ENODEV loop. This qualifies
the listener path on one development handset, not every DSP compute workload,
suspend scenario or another firmware revision. No new SELinux allow is needed.
