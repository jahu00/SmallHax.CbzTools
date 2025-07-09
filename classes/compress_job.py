import re
import os
from zipfile import ZipFile
import logging

logger = logging.getLogger(__name__)


class CompressJob():
    def __init__(self, src_path: str, dst_path: str, src_name: str = None, dst_name: str = None):
        self.src_path = src_path
        self.dst_path = dst_path
        self.src_name = src_name or os.path.basename(src_path)
        self.dst_name = dst_name or os.path.basename(dst_path)

    def compress(self):
        logger.debug(f"Creating file: {self.dst_path}")
        with ZipFile(self.dst_path, "w") as zf:
            logger.debug(f"Scanning: {self.src_path}")
            for root, dirs, files in self.walk(self.src_path):
                for file in files:
                    path = os.path.join(root, file)
                    logger("Writing file: {path} => {file}")
                    zf.write(path, arcname=file)

    @staticmethod
    def walk(path):
        children = os. listdir(path)
        #children.sort()
        dirs = []
        files = []
        for child in children:
            child_path = os.path.join(path, child)
            if os.path.isdir(child_path):
                dirs += child
            else:
                files.append(child)

        yield (path, dirs, files)
        for dir in dirs:
            dir_path = os.path.join(path, dir)
            yield from CompressJob.walk(dir_path)
        

    @staticmethod
    def get_jobs(path, dst, rule = None, replace = None):
        jobs = []
        children = os. listdir(path)
        children.sort()
        for child in children:
            child_path = os.path.join(path, child)
            if not os.path.isdir(child_path):
                continue

            job = CompressJob.get_job(child_path, dst, rule, replace)
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
