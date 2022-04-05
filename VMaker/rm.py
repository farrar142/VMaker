
import os
import shutil


def force_rmdir(path):
    if path != ".":
        try:
            shutil.rmtree(path)
        except:
            pass


def force_rm(path):
    try:
        os.remove(path)
    except:
        pass


def force_mkdir(path):
    force_rmdir(path)
    try:
        os.mkdir(path)
    except:
        pass


def force_cp(origin, changed):
    try:
        shutil.move(changed, origin)
    except:

        pass
