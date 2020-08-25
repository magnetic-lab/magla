"""This script overwrites the default TouchDesigner menu with a custom one.

Meant to be run as a startup-script.
"""
import os
import shutil
import platform

from magla import MaglaConfig, MaglaTool

__SYSTEM = platform.system().lower()
if __SYSTEM == "windows":
    import win32file


def startup():
    """Execute startup processes."""
    return True


def __backup_and_overwrite(src, dst):
    """create backup before deleting - in this case dst is the src and the backup is the dst.

        :param src: source path
        :param dst: destination path
    """
    filepath, ext = os.path.splitext(dst)
    shutil.copyfile(dst, filepath + "_backup" + ext)
    os.remove(dst)

    if __SYSTEM == "windows":
        win32file.CreateSymbolicLink(dst, src, 0)
    else:
        os.symlink(src, dst)

    return True


def main():
    """Execute this startup script."""
    result
    try:
        result = startup()
    except Exception, e:
        result = e

    return result
