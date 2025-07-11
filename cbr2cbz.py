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

def verbose_print(*args):
    if verbose:
        print("[VERBOSE]", *args)

def convert_files(input_file, target_path=None, temp_path=None, delete_original=False):
    command = find_7z_executable()
    if command is None:
        print("7z is not installed or not in the system PATH.")
        sys.exit(1)

    print("7z executable found: ", command)

    if os.path.isdir(input_file):
        print("Directory is not allowed as source. Only file or mask is allowed.")
        sys.exit(1)

    directory = os.path.dirname(input_file)
    verbose_print("Input directory: ", directory)
    mask = os.path.basename(input_file)
    verbose_print("Input file mask: ", mask)
    if target_path is None:
        target_path = directory

    if temp_path is None:
        if os.path.isdir(target_path):
            temp_path = target_path
        else:
            temp_path = os.path.dirname(target_path)

    temp_dir = temp_path
    verbose_print("Temporary directory: ", temp_dir)

    filter = lambda x,y: x == y
    if mask.startswith("*") and mask.endswith("*"):
        filter = lambda x, y: x.contains(y.replace("*", ""))
    elif mask.startswith("*"):
        filter = lambda x, y: x.endswith(y.replace("*", ""))
    elif mask.endswith("*"):
        filter = lambda x, y: x.startswith(y.replace("*", ""))

    for file_path in [f for f in os.listdir(directory) if filter(f, mask)]:
        source_file = os.path.join(directory, file_path)
        print(f"Processing file: {source_file}")
        file_name = os.path.splitext(os.path.basename(source_file))[0]
        output_dir = os.path.join(temp_dir, str(uuid.uuid4()))

        verbose_print("Creating output directory: ", output_dir)
        os.makedirs(output_dir, exist_ok=False)

        verbose_print("Extracting archive: ", source_file)
        subprocess.run([command, "x", source_file, "-o" + output_dir], check=True)

        # Compress the extracted files into a ZIP file
        if os.path.isdir(target_path):
            zip_file = os.path.join(target_path, f"{file_name}.cbz")
        else:
            zip_file = target_path
        verbose_print("Creating archive: ", zip_file)
        subprocess.run([command, "a", "-tzip", zip_file, os.path.join(output_dir, "*")], check=True)

        verbose_print("Delete output directory: ", output_dir)
        # Clean up the extracted files
        shutil.rmtree(output_dir)

        # Delete the source file if the switch is set
        if delete_original:
            os.remove(source_file)

    print(f"Conversion complete: {zip_file}")

verbose = False

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Convert RAR to CBZ using 7z.")
    parser.add_argument("--src", type=str, help="Input file or directory with mask", required=True)
    parser.add_argument("--dst", type=str,help="Output file name or directory", required=False, default=None)
    parser.add_argument("--tempDir", type=str, required=False, default=None, help="Temporary directory for extraction")
    parser.add_argument("-d", "--delete", action="store_true", help="Delete the source file after conversion")
    parser.add_argument("-v", "--verbose", action="store_true", help="verbose output")

    args = parser.parse_args()
    verbose = args.verbose
    convert_files(args.src, args.dst, temp_path=args.tempDir, delete_original=args.delete)