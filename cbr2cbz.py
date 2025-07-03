import os
import shutil
import subprocess
import sys
import uuid

def find_7z_executable():
    commands = ["7z", "7zz", "7za"]
    for command in commands:
        if is_7z_installed(command):
            return command
    return None


def is_7z_installed(command):
    """Check if 7z is installed."""
    try:
        subprocess.run([command], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def convert_files(input_file, target_path=None, temp_path=None, delete_original=False):
    command = find_7z_executable()
    if command is None:
        print("7z is not installed or not in the system PATH.")
        sys.exit(1)

    print("7z executable found: ", command)

    directory = os.path.dirname(input_file)
    mask = os.path.basename(input_file)
    if target_path is None:
        target_path = directory

    if temp_path is None:
        temp_path = os.path.dirname(target_path)
    
    temp_dir = os.path.join(temp_path, str(uuid.uuid4()))

    for file_path in [f for f in os.listdir(directory) if f.endswith(mask)]:
        source_file = os.path.join(directory, file_path)
        print(f"Processing file: {source_file}")
        file_name = os.path.splitext(os.path.basename(source_file))[0]
        output_dir = os.path.join(temp_dir, file_name)

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        # Extract the RAR file
        subprocess.run([command, "x", source_file, "-o" + output_dir], check=True)

        # Compress the extracted files into a ZIP file
        if os.path.isdir(target_path):
            zip_file = os.path.join(target_path, f"{file_name}.cbz")
        else:
            zip_file = target_path
        subprocess.run([command, "a", "-tzip", zip_file, os.path.join(output_dir, "*")], check=True)

        # Clean up the extracted files
        shutil.rmtree(temp_dir)

        # Delete the source file if the switch is set
        if delete_original:
            os.remove(source_file)

        print(f"Conversion complete: {zip_file}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Convert RAR to CBZ using 7z.")
    parser.add_argument("--src", type=str, help="Input file or directory with mask", required=True)
    parser.add_argument("--dst", type=str,help="Output file name or directory", required=False, default=None)
    parser.add_argument("--tempDir", type=str, required=False, default=None, help="Temporary directory for extraction")
    parser.add_argument("-d", "--delete", action="store_true", help="Delete the source file after conversion")

    args = parser.parse_args()

    convert_files(args.src, args.dst, temp_path=args.tempDir, delete_original=args.delete)