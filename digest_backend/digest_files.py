from evaluation.mappers.mapper import FileMapper as digest_files
import os

fileDir = "/usr/src/digest/mapping_files"


def fileSetupComplete():
    csv_needed = list(i for i in digest_files.file_names.values() if i.endswith(".csv"))
    jaccard_needed = list(i for i in digest_files.file_names.values() if not i.endswith(".csv"))
    overlap_needed = list(i for i in digest_files.file_names.values() if not i.endswith(".csv"))
    print(csv_needed)
    print(jaccard_needed)
    print(overlap_needed)
    checkExistingFiles(csv_needed, fileDir)
    dir_jaccard = os.path.join(fileDir, "jaccard")
    checkExistingFiles(jaccard_needed, dir_jaccard)
    dir_overlap = os.path.join(fileDir, "overlap")
    checkExistingFiles(overlap_needed, dir_overlap)
    return (len(csv_needed) + len(jaccard_needed) + len(overlap_needed)) == 0


def checkExistingFiles(files, fileDir):
    if os.path.exists(fileDir):
        for file in os.listdir(fileDir):
            if file in files:
                files.remove(file)
    return files


def getFile(name):
    file = os.path.join(fileDir, name)
    if os.path.exists(file):
        return file
    else:
        return None
