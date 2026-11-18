# Pong 6.18.64 RC source attribution

Szmazwidi maintains and co-develops the Pong port, supplies the hardware and
integration baseline, and evaluates device behavior. OpenAI Codex contributed
the 6.18.64 integration, local adaptations, verification and this build recipe.
Claude's previous contributions remain in the existing history.

## Kernel and modules

The stable merge retains the exact Linux
[v6.18.64 commit](https://github.com/Szmazwidi/android_kernel_nothing_sm8475-6.18/commit/fd7cfd39c88596fec816639ad83cbf3e9d316372)
and the original signed tag. Its 695 incoming commits retain their IDs,
authors, commit messages, and existing trailers. The tag signature was
verified using Greg Kroah-Hartman's kernel.org key.

The Pong
[merge](https://github.com/Szmazwidi/android_kernel_nothing_sm8475-6.18/commit/98f1e3a2be1e8469a3b20d30d19d7a24bcd52256)
adapts the stable changes to the retained Android memory, block-I/O,
fs-verity and protected-KVM interfaces.
The subsequent
[F2FS caller fix](https://github.com/Szmazwidi/android_kernel_nothing_sm8475-6.18/commit/febb385ea217722658e25cebffc2e79171be69c7)
threads the caller-owned superblock through the warm-node helper. Its
stable prerequisite is Chao Yu's
`ecf2796547582f1518f36bba370904934e659a46`.

The [module history](https://github.com/Szmazwidi/android_kernel_nothing_sm8475-modules-6.18/tree/pong-a17-6.18.64-rc)
carries the existing Qualcomm, Nothing, redducc and Pong work. The .64 changes
pin the kernel revision and extend the existing version-aware build
preflight. The .63
[attribution record](../community-6.18.63-wlan-fastrpc/README.md)
links the earlier Android, Rust, xHCI, WLAN and FastRPC work.

## Android userspace

The Android build takes the Qualcomm audio and display UAPI headers from
the [Pong-Development module tree at the pinned revision](https://github.com/Pong-Development/kernel_nothing_sm8475-modules/tree/ab6a3a7461ea649faea4151952acb6cf3165a891).
The two header directories match the Git trees used by the earlier working build.

The device-tree integration retains the author metadata of donor commits,
including Ghosuto's DeviceExtras, ADPF, thermal and power-hint work and the
display and Bluetooth contributors. The local follow-ups retain their
existing authors and messages. The new documentation and integration merge
identify Szmazwidi and OpenAI Codex together.

The snapshot stores the original commit authors and full messages for the
additional power-HAL, Pixel libperfmgr and update-engine source deltas in
`patches/series.json`. The recorded Ghosuto-authored patches retain that
metadata. The update-engine signature-verification revert retains its
OpenAI Codex attribution and original revert reference.

The patch bundle reconstructs the tested source trees on public upstream
bases. It leaves the upstream history intact. Building from these snapshots
does not confer ownership of the imported code or change its license.
