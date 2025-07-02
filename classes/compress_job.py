import re
import os
from zipfile import ZipFile

class CompressJob():
    def __init__(self, src_path: str, dst_path: str, src_name: str = None, dst_name: str = None):
        self.src_path = src_path
        self.dst_path = dst_path
        self.src_name = src_name or os.path.basename(src_path)
        self.dst_name = dst_name or os.path.basename(dst_path)

    def compress(self):
        with ZipFile(self.dst_path, "w") as zf:
            for root, dirs, files in os.walk(self.src_path):
                for file in files:
                    zf.write(os.path.join(root, file), arcname=file)

    @staticmethod
    def get_jobs(path, dst, rule = None, replace = None):
        jobs = []
        subfolders = os. listdir(path)
        subfolders.sort()
        for folder in subfolders:
            if not os.path.isdir(os.path.join(path, folder)):
                continue

            job = CompressJob.get_job(folder, dst, rule, replace)
            jobs.append(job)
        
        return jobs

    @staticmethod
    def get_job(src, dst, rule = None, replace = None):
        src_name = os.path.basename(src)
        dst_name = src_name + ".cbz"
        if rule:
            dst_name = re.sub(rule, replace, src_name)

        src_path = src
        dst_path = os.path.join(dst, dst_name)
        return CompressJob(src_path, dst_path, src_name, dst_name)
