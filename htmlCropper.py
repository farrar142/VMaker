from subprocess import Popen, PIPE
import os
import sys
import ffmpeg
from screeninfo import get_monitors
from pathlib import Path as p
from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

import sys
path = str(p(__file__).parent)
sys.path.append(path)


def get_monitor_size(idx=0):
    monitors = sorted(get_monitors(), key=lambda x: x.width, reverse=True)
    return monitors[idx].width, monitors[idx].height


width, height = get_monitor_size()
time = 10


def set_chrome_driver():
    chrome_options = Options()  # 인스턴스 생성
    chrome_options.add_argument("--headless")  # 내부적으로 실행
    chrome_options.add_argument(f"--window-size={width},{height}")
    driver = webdriver.Chrome(service=Service(
        ChromeDriverManager().install()), options=chrome_options)
    return driver


saveto = "./intro.jpeg"
# url = "https://google.com"
# driver: Chrome = set_chrome_driver()
# driver.get(url)
# driver.implicitly_wait(5)
# driver.save_screenshot(saveto)


def img_to_vid(img, length, width, height, output):
    i_to_v = f"ffmpeg -loop 1 -y -i {img} -c:v libx264 -t {length} -pix_fmt yuv420p -vf scale={width}:{height} {output}"

    p = Popen(i_to_v.split(" "),
              stdin=PIPE)


img_to_vid(saveto, 15, width, height, 'intro.mp4')
