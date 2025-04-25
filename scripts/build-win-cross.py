import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

versions_json = os.environ.get('VERSIONS', '[]')
versions = json.loads(versions_json)
runner_os = os.environ.get('RUNNER_OS')
arch = os.environ.get('ARCH')
ext = os.environ.get('EXT', '')
crs = os.environ.get('CRS', '')

print(f"Initial working directory: {os.getcwd()}")
root_dir: Path = Path(__file__).parent.parent
os.chdir(root_dir)

print(f"Working directory after initial change: {os.getcwd()}")

if runner_os == 'Windows':
    make_command = 'make'
elif runner_os == 'Linux' or runner_os == 'macOS':
    make_command = 'make'
else:
    print(f"Unsupported OS: {runner_os}")
    sys.exit(1)

for version in versions:
    print(f"\nBuilding for CircuitPython version: {version}")

    try:
        # Sync submodule
        subprocess.run(['git', 'submodule', 'update', '--init'], check=True)
        print(f"Working directory after submodule update: {os.getcwd()}")

        # Checkout specific version
        os.chdir('./circuitpython')
        print(f"Working directory after chdir to ./circuitpython: {os.getcwd()}")
        subprocess.run(['git', 'fetch', 'origin', version, '--depth=1'], check=True)
        subprocess.run(['git', 'checkout', version], check=True)
        os.chdir('..')
        print(f"Working directory after checkout and chdir back: {os.getcwd()}")

        # Build mpy-cross
        if runner_os == 'Windows':
            subprocess.run([make_command, '-C', './circuitpython/mpy-cross', 'clean'], check=True)
            subprocess.run([crs, make_command, '-C', './circuitpython/mpy-cross'], check=True)
            source_file = Path(f"./circuitpython/mpy-cross/build/mpy-cross{ext}")
            destination_dir = root_dir / "archive" / "windows" / arch / version
            os.makedirs(destination_dir, exist_ok=True)
            destination_path = destination_dir / f"mpy-cross{ext}"
            if source_file.exists():
                shutil.copy2(source_file, destination_path)
                print(f"Copied {source_file} to {destination_path}")
            else:
                print(f"Source file not found: {source_file}")

    except subprocess.CalledProcessError as e:
        print(f"Error building version {version}: {e}")
        print(f"Continuing to the next version.")

    except Exception as e:
        print(f"An unexpected error occurred while building version {version}: {e}")
        print(f"Continuing to the next version.")

[print(p) for p in (root_dir / "archive" / "windows").iterdir()]

print("Build process completed for all versions.")
