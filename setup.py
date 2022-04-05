import os
import sys
from pathlib import Path

vmaker = Path(os.getcwd()).joinpath('VMaker')
site_packages = Path(sys.executable).parent.joinpath(
    'Lib').joinpath("site-packages")
sp_vm = site_packages.joinpath("VMaker")
sp_pty = site_packages
youtube_api = Path(os.getcwd()).joinpath('PyToYou')
modules = ["googleapiclient", "apiclient"]
try:
    os.symlink(vmaker, sp_vm)
    print(f"{sp_vm} success")
except:
    print(f"{sp_vm} failed")
try:
    for i in modules:
        try:
            os.symlink(youtube_api.joinpath(i), sp_pty.joinpath(i))
            print(f"{i} success")
        except:
            print(f"{i} failed")
except:
    pass
