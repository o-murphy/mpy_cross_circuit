import re

import boto3
from botocore import UNSIGNED
from botocore.config import Config

# Create an anonymous S3 client
s3 = boto3.client("s3", config=Config(signature_version=UNSIGNED))

bucket_name = "adafruit-circuit-python"

prefixes = {
    "linux-aarch64": "bin/mpy-cross/linux-aarch64/",
    "linux-amd64": "bin/mpy-cross/linux-amd64/",
    "linux-raspbian": "bin/mpy-cross/linux-raspbian/",
    "macos-11": "bin/mpy-cross/macos-11/",
    "macos": "bin/mpy-cross/macos/",
    "windows": "bin/mpy-cross/windows/",
}

version_pattern = re.compile(
    r"""mpy-cross(?:-[^-/]+)?[-.]           # prefix and optional short target
    (?:(?:linux|macos|windows)-[^-/]+[-.])? # optional full target
    (?P<version>\d+\.\d+\.\d+(?:-(?:alpha|beta|rc)\.\d+(?:-\d+-\w+)?)?) # version
    (?:[-.](?:static(?:-[^/.]+)?))?       # optional static arch
    (?:-(?:arm64|x64|universal))?        # optional platform arch
    (?:-(?P<git_hash>[0-9a-f]{7,}))?     # optional git hash
    """,
    re.VERBOSE,
)

version_pattern_legacy_static = re.compile(
    r"mpy-cross\.static-[^-]+-(?P<version_legacy>\d+\.\d+\.\d+(?:-rc\.\d+)?)$"
)

version_pattern_macos = re.compile(
    r"mpy-cross-macos-\d+-(?P<version_macos>\d+\.\d+\.\d+(?:-(?:alpha|beta|rc)\.\d+(?:-\d+-\w+)?)?)-(?:arm64|universal|x64)$"
)

version_pattern_macos_legacy = re.compile(
    r"mpy-cross-macos-\w+-(?P<version_macos_legacy>\d+\.\d+\.\d+(?:-(?:alpha|beta|rc)\.\d+)?)-(?:arm64|universal|x64)$"
)


def extract_version(name):
    if match := version_pattern.search(name):
        return match.group("version")
    if match_legacy := version_pattern_legacy_static.search(name):
        return match_legacy.group("version_legacy")
    if match_macos := version_pattern_macos.search(name):
        return match_macos.group("version_macos")
    if match_macos_legacy := version_pattern_macos_legacy.search(name):
        return match_macos_legacy.group("version_macos_legacy")
    return None


def filter_versions(versions):
    """
    Filters a list of version strings to remove those with build numbers or commit hashes,
    but keeps stable, alpha, beta, and rc versions.

    Args:
        versions: A list of version strings (e.g., ["9.2.0", "9.2.1-5-g7d8e41fe4d", "10.0.0-alpha.2-12", "10.0.0-alpha.2", "10.0.0-rc.1"]).

    Returns:
        A list of version strings that do not contain build numbers or commit hashes,
        but includes stable, alpha, beta, and rc versions (e.g., ["9.2.0", "10.0.0-alpha.2", "10.0.0-rc.1"]).
    """
    filtered_versions = []
    for version in versions:
        parts = version.split('-')
        if len(parts) == 1:
            # This is a stable version, keep it.
            filtered_versions.append(version)
        elif len(parts) > 1 and parts[1].split('.')[0] in ('alpha', 'beta', 'rc'):
            #  This is an alpha, beta, or rc version.  Check if it has a build number
            if len(parts) == 2:
                filtered_versions.append(version)  # no build number
            elif len(parts) == 3 and not parts[2].startswith('g'):
                filtered_versions.append(version)  # no git hash
    return filtered_versions


def fetch_versions():
    actual_versions = []
    for platform, prefix in prefixes.items():
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)

        for obj in response.get("Contents", []):
            filename = obj["Key"].split('/')[-1]
            if version := extract_version(filename):
                if version not in actual_versions:
                    actual_versions.append(version)

    # Filter the versions *after* they've been extracted
    clean_versions = filter_versions(actual_versions)
    return sorted(list(clean_versions))


if __name__ == "__main__":
    print(fetch_versions())
