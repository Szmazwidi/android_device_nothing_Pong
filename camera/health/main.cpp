// SPDX-License-Identifier: Apache-2.0
// Observe public camera enumeration; never open a camera or capture user data.
#include <android/binder_process.h>
#include <android/log.h>
#include <camera/NdkCameraManager.h>
#include <sys/system_properties.h>
#include <chrono>
#include <cstring>
#include <thread>

int main(int argc, char** argv) {
    const bool check = argc == 2 && !std::strcmp(argv[1], "--check");
    if (!check && (argc != 2 || std::strcmp(argv[1], "--watch"))) return 64;
    ABinderProcess_setThreadPoolMaxThreadCount(2);
    ABinderProcess_startThreadPool();
    ACameraManager* manager = ACameraManager_create();
    if (!manager) return 1;
    const auto end = std::chrono::steady_clock::now() + std::chrono::seconds(check ? 0 : 20);
    int count = 0;
    do {
        ACameraIdList* ids = nullptr;
        const auto status = ACameraManager_getCameraIdList(manager, &ids);
        count = status == ACAMERA_OK && ids ? ids->numCameras : 0;
        if (ids) ACameraManager_deleteCameraIdList(ids);
        // Main and front are public; auxiliary physical/logical IDs can be private.
        if (count >= 2) {
            __android_log_print(ANDROID_LOG_INFO, "PongCameraHealth", "public cameras ready: %d", count);
            ACameraManager_delete(manager);
            return 0;
        }
        if (check || std::chrono::steady_clock::now() >= end) break;
        std::this_thread::sleep_for(std::chrono::milliseconds(500));
    } while (true);
    ACameraManager_delete(manager);
    __android_log_print(ANDROID_LOG_WARN, "PongCameraHealth", "public cameras not ready: %d", count);
    if (check) return 1;
    // Init owns the once-per-boot latch and service restart. This process has
    // no ctl.* permission, module loading, camera-open or data-file access.
    if (__system_property_set("sys.pong.camera.refresh_needed", "1") != 0) return 2;
    return 0;
}
