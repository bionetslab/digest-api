from mappers.mapper import FileMapper as digest_files
import os

fileDir = "/usr/src/digest/mapping_files"

def fileSetupComplete():
    needed = list(digest_files.file_names.values())
    print(needed)
    if os.path.exists(fileDir):
        for file in os.listdir(fileDir):
            if file in needed:
                needed.remove(file)
    return len(needed)==0


def getFile(name):
    file = os.path.join(fileDir,name)
    if os.path.exists(file):
        return file
    else:
        return None