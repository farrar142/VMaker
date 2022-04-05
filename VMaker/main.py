import os
import sys
from pathlib import Path as p
# os.chdir(os.getcwd())
# try:
#     os.chdir(sys._MEIPASS)
#     print(sys._MEIPASS)
# except:
#     os.chdir(os.getcwd())
sys.path.append(str(p(__file__).parent.parent))
if True:
    from .File import File
    from . import concat


def run():
    files_2 = File.get_mp4_files()
    concat.main(files_2)
    print(os.getcwd())
