import argparse
import zipfile


def fields(archive, name, keys):
    if archive.namelist().count(name) != 1:
        raise ValueError(f"Missing or ambiguous {name}")
    values = {}
    for line in archive.read(name).decode().splitlines():
        key, sep, value = line.partition("=")
        if sep and key in keys:
            if key in values or not value:
                raise ValueError(f"Invalid {key} in {name}")
            values[key] = value
    if values.keys() != set(keys):
        raise ValueError(f"Missing fields in {name}: {set(keys) - values.keys()}")
    return [values[key] for key in keys]


def identity(path, target_files=False):
    with zipfile.ZipFile(path) as archive:
        if target_files:
            candidates = [name for name in ("SYSTEM/build.prop", "SYSTEM/system/build.prop")
                          if name in archive.namelist()]
            if len(candidates) != 1:
                raise ValueError("Ambiguous system build properties")
            timestamp, number = fields(archive, candidates[0],
                                       ("ro.build.date.utc", "ro.build.version.incremental"))
        else:
            kind, device, timestamp, number = fields(
                archive, "META-INF/com/android/metadata",
                ("ota-type", "pre-device", "post-timestamp", "post-build-incremental"))
            if kind != "AB" or device != "Pong":
                raise ValueError("Expected a Pong A/B OTA")
    if not all(value.isascii() and value.isdecimal() and str(int(value)) == value
               and int(value) > 0 for value in (timestamp, number)):
        raise ValueError("Expected positive canonical numeric Pong release identifiers")
    return int(timestamp), int(number)


def check(candidate, previous=None, target_files=False):
    current = identity(candidate, target_files)
    if previous is not None:
        old = identity(previous)
        if current[0] <= old[0] or current[1] <= old[1]:
            raise ValueError(f"Release collision or rollback: previous {old}, candidate {current}")
    return current


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check a candidate against the last released Pong OTA")
    parser.add_argument("previous")
    parser.add_argument("candidate")
    parser.add_argument("--target-files", action="store_true")
    args = parser.parse_args()
    try:
        print(check(args.candidate, args.previous, args.target_files))
    except (ValueError, OSError, zipfile.BadZipFile) as error:
        parser.exit(1, f"{error}\n")
