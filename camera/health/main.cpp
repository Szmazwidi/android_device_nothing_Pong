// SPDX-License-Identifier: Apache-2.0
// Observe public camera enumeration; never open a camera or capture user data.
#include <android/content/AttributionSourceState.h>
#include <android/hardware/ICameraService.h>
#include <binder/IServiceManager.h>
#include <android/log.h>
#include <sys/system_properties.h>
#include <chrono>
#include <cstring>
#include <thread>
#include <unistd.h>

int main(int argc, char** argv) {
    const bool check = argc == 2 && !std::strcmp(argv[1], "--check");
    if (!check && (argc != 2 || std::strcmp(argv[1], "--watch"))) return 64;
    // Ask the platform service directly: NDK camera enumeration maintains a
    // listener and needs callbacks from cameraserver. This observer needs no
    // callbacks, camera-open permissions or virtual-device service access.
    android::content::AttributionSourceState attribution;
    attribution.uid = getuid();
    attribution.pid = getpid();
    attribution.deviceId = 0;  // Default physical device, not a virtual camera.
    const auto end = std::chrono::steady_clock::now() + std::chrono::seconds(check ? 0 : 20);
    int count = 0;
    do {
        const auto binder = android::defaultServiceManager()->checkService(
                android::String16("media.camera"));
        const auto service = android::interface_cast<android::hardware::ICameraService>(binder);
        int32_t available = 0;
        if (service != nullptr) {
            const auto status = service->getNumberOfCameras(
                    android::hardware::ICameraService::CAMERA_TYPE_BACKWARD_COMPATIBLE,
                    attribution, 0 /* DEVICE_POLICY_DEFAULT */, &available);
            if (status.isOk()) count = available;
            else count = 0;
        } else {
            count = 0;
        }
        // Main and front are public; auxiliary physical/logical IDs can be private.
        if (count >= 2) {
            __android_log_print(ANDROID_LOG_INFO, "PongCameraHealth", "public cameras ready: %d", count);
            return 0;
        }
        if (check || std::chrono::steady_clock::now() >= end) break;
        std::this_thread::sleep_for(std::chrono::milliseconds(500));
    } while (true);
    __android_log_print(ANDROID_LOG_WARN, "PongCameraHealth", "public cameras not ready: %d", count);
    if (check) return 1;
    // Init owns the once-per-boot latch and service restart. This process has
    // no ctl.* permission, module loading, camera-open or data-file access.
    if (__system_property_set("sys.pong.camera.refresh_needed", "1") != 0) return 2;
    return 0;
}
