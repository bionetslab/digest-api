import os

from setup import main as digest_setup
from mappers.mapper import FileMapper as digest_files
import single_validation
# from application.setup import main as digest_setup
# from application.mappers.mapper import FileMapper as digest_files



def setup(self):
    print("starting setup!")
    digest_setup()


def check(self):
    needed = list(digest_files.file_names.values())
    for file in os.listdir("/usr/src/digest/mapping_files"):
        if file in needed:
            needed.remove(file)
    if len(needed) > 0:
        setup(self)
    else:
        print("Setup fine! All files are already there.")

def clear(self):
    for file in os.listdir("/usr/src/digest/mapping_files"):
        os.remove("/usr/src/digest/mapping_files"+file)


def validate(r, ri, t, ti, m):
    single_validation()