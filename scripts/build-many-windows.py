import os
import shutil
import json
import subprocess
import sys  # Import the sys module

versions_json = os.environ.get('VERSIONS', '[]')
versions = json.loads(versions_json)
runner_os = os.environ.get('RUNNER_OS')
arch = os.environ.get('ARCH')
ext = os.environ.get('EXT', '')
crs = os.environ.get('CRS', '')

if runner_os == 'Windows':
    make_command = 'make'
elif runner_os == 'Linux' or runner_os == 'macOS':
    make_command = 'make'
else:
    print(f"Unsupported OS: {runner_os}")
    exit(1)

for version in versions:
    print(f"Building for CircuitPython version: {version}")

    version_build_dir = f"build_{version}"
    os.makedirs(version_build_dir, exist_ok=True)
    os.chdir(version_build_dir)

    try:
        # Sync submodule
        subprocess.run(['git', 'submodule', 'update', '--init'], check=True)

        # Checkout specific version
        os.chdir('./circuitpython')
        subprocess.run(['git', 'fetch', 'origin', version, '--depth=1'], check=True)
        subprocess.run(['git', 'checkout', version], check=True)
        os.chdir('..')

        # Build mpy-cross
        if runner_os == 'Windows':
            subprocess.run([make_command, '-C', './circuitpython/mpy-cross', 'clean'], check=True)
            subprocess.run([crs, make_command, '-C', './circuitpython/mpy-cross'], check=True)
            source_file = f"./circuitpython/mpy-cross/build/mpy-cross{ext}"
            destination_dir = os.path.join("..", "archive", "windows", arch, version)
            os.makedirs(destination_dir, exist_ok=True)
            destination_path = os.path.join(destination_dir, f"mpy-cross{ext}")
            if os.path.exists(source_file):
                shutil.copy2(source_file, destination_path)
                print(f"Copied {source_file} to {destination_path}")
            else:
                print(f"Source file not found: {source_file}")

    except subprocess.CalledProcessError as e:
        print(f"Error building version {version}: {e}")
        print(f"Continuing to the next version.")
        # Optionally, you might want to log the error to a file.
        # with open("build_errors.log", "a") as f:
        #     f.write(f"Error building version {version}: {e}\n")

    except Exception as e:
        print(f"An unexpected error occurred while building version {version}: {e}")
        print(f"Continuing to the next version.")

    os.chdir('..')  # Back to workflow root

print("Build process completed for all versions.")