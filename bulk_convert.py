import argparse
import os
import re
from zipfile import ZipFile


parser = argparse.ArgumentParser(description="Attempts to make a cbz file out of every folder at a given path")
parser.add_argument("--path", type=str, help="source path", required=True)
parser.add_argument("--dst", type=str, help="destination path", default=None, required=False)
parser.add_argument("--rule", type=str, help="regex replace rule for directory names", default=None, required=False)
parser.add_argument("--replace", type=str, help="allow move operation", default=None, required=False)
parser.add_argument("--confirmn", type=int, help="automatically confirm", default=False, required=False)

args = parser.parse_args()
dst = args.dst or args.path
subfolders = os. listdir(args.path)
items = []
for folder in subfolders:
    name = os.path.basename(folder)
    dst_name = name + ".cbz"
    if args.rule:
        dst_name = re.sub(args.rule, args.replace, name)

    src_path = os.path.join(args.path, folder)
    dst_path = os.path.join(dst, dst_name)
    items.append((src_path, dst_path))

# sort items by source path
items.sort(key=lambda x: x[0])

for item in items:
    print(item[0] + "->" + item[1])

if not args.confirmn:
    confirm = input("Apply operations? (y/n) ").lower() == "y"

    if not confirm:
        print("Exiting without applying operations.")
        exit()

for item in items:
    with ZipFile(item[1], "w") as zf:
        for root, dirs, files in os.walk(item[0]):
            for file in files:
                zf.write(os.path.join(root, file), arcname=file)
                
    print("Created " + item[1])
    
print("Done.")