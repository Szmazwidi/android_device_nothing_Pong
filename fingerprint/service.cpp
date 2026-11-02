/*
 * Copyright (C) 2024 The LineageOS Project
 *
 * SPDX-License-Identifier: Apache-2.0
 */

#include "Fingerprint.h"

#include <android/binder_manager.h>
#include <android/binder_process.h>
#include <android-base/logging.h>

using ::aidl::android::hardware::biometrics::fingerprint::Fingerprint;

int main() {
    ABinderProcess_setThreadPoolMaxThreadCount(0);
    std::shared_ptr<Fingerprint> fingerprint = ndk::SharedRefBase::make<Fingerprint>();
    // Do not advertise a live Binder endpoint for unavailable hardware. Let
    // init's bounded restart interval retry opening it instead of causing a
    // tight framework createSession/DEAD_OBJECT retry loop.
    if (!fingerprint->isHardwareReady()) {
        LOG(ERROR) << "Fingerprint hardware is not ready; defer service registration";
        return EXIT_FAILURE;
    }

    const std::string instance = std::string() + Fingerprint::descriptor + "/default";
    binder_status_t status = AServiceManager_addService(fingerprint->asBinder().get(), instance.c_str());
    CHECK(status == STATUS_OK);

    ABinderProcess_joinThreadPool();
    return EXIT_FAILURE; // should not reach
}
