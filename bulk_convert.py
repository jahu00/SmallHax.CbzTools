import argparse
import logging
import sys
from classes import CompressJob


parser = argparse.ArgumentParser(description="Makes a cbz file out of every folder at a given path")
parser.add_argument("--path", type=str, help="source path", required=True)
parser.add_argument("--dst", type=str, help="destination path", default=None, required=False)
parser.add_argument("--rule", type=str, help="regex replace rule for directory names", default=None, required=False)
parser.add_argument("--replace", type=str, help="replace template", default=None, required=False)
parser.add_argument("--confirm", type=int, help="automatically confirm", default=False, required=False)
parser.add_argument("-v", "--verbose", action="store_true", help="verbose output")

args = parser.parse_args()
verbose = args.verbose
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG if args.verbose else logging.INFO)
dst = args.dst or args.path
jobs = CompressJob.get_jobs(args.path, dst, args.rule, args.replace)

for job in jobs:
    print(job.src_name + "->" + job.dst_name)

if not args.confirm:
    confirm = input("Apply operations? (y/n) ").lower() == "y"

    if not confirm:
        print("Exiting without applying operations.")
        exit()

for job in jobs:
    job.compress()
    print("Created " + job.dst_path)
    
print("Done.")