import json
import re

import semver

versions = [
    '10.0.0-alpha.2',
    '8.0.2',
    '8.1.0',
    '8.2.10',
    '9.0.0',
    '9.1.4',
    '9.2.7',
]

__versions__ = [(v, v) for v in versions]
__lookup = {v[1]: v[0] for v in __versions__}


def find_closest_version(target_version):
    """
    Finds the closest version from a list based on a semantic version comparison
    specified within the target_version string (e.g., '>=9.0.1').  If no operator
    is given, defaults to '=='.

    Args:
        target_version (str): The target version string, optionally including the
            comparison operator (e.g., '>', '>=', '<', '<=', '==') at the
            beginning.  If no operator is present, '==' is assumed.

    Returns:
        str: The closest matching version, or None if no match is found.
    """
    closest_version = None
    closest_distance = None
    operator_match = re.match(r"^(>=|<=|>|<|==)?(.+)$", target_version)

    if not operator_match:
        print(f"Error: Invalid target version format: {target_version}. "
              "Expected optional operator (>=, <=, >, <, ==) followed by the version.")
        return None

    comparison_operator = operator_match.group(1)
    version_part = operator_match.group(2).strip()

    if not comparison_operator:
        comparison_operator = "=="

    try:
        parsed_target = semver.VersionInfo.parse(version_part)

        for version_string in __lookup:
            try:
                parsed_version = semver.VersionInfo.parse(version_string)

                match = False
                if comparison_operator == '>':
                    match = parsed_version > parsed_target
                elif comparison_operator == '>=':
                    match = parsed_version >= parsed_target
                elif comparison_operator == '<':
                    match = parsed_version < parsed_target
                elif comparison_operator == '<=':
                    match = parsed_version <= parsed_target
                elif comparison_operator == '==':
                    match = parsed_version == parsed_target

                if match:
                    distance = abs(parsed_target.major - parsed_version.major) + \
                               abs(parsed_target.minor - parsed_version.minor) + \
                               abs(parsed_target.patch - parsed_version.patch)

                    if closest_version is None or distance < closest_distance:
                        closest_version = version_string
                        closest_distance = distance
            except ValueError as e:
                print(f"Error comparing version {version_string}: {e}")
                pass
    except ValueError as e:
        print(f"Error parsing target version {version_part}: {e}")
        return None

    return closest_version


def mpy_version(circuitpython: str, bytecode: str):
    ret = None
    if circuitpython:
        ret = find_closest_version(circuitpython)
    elif bytecode:
        ret = __lookup.get(bytecode.lower().strip("v"))

    if not ret:
        raise SystemExit(f"Error: Couldn't identify {circuitpython or bytecode} in known versions: \n{__versions__}")
    return ret


if __name__ == "__main__":
    import sys

    if "-b" in sys.argv:
        print(
            " ".join(dict(__versions__).values())
        )
    elif "--json" in sys.argv:
        print(json.dumps(versions))
    else:
        print()
        print(
            " ".join(dict(__versions__).keys())
        )
