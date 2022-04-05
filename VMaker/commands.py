
import json
import os
import subprocess
import logzero
from logzero import logger


def run_cmd(args: list[str]):
    """
    PIPE를 통해 결과값을 받아옵니다.\n
    json을 파싱한 값을 리턴합니다.
    """

    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    logging(p, args)
    try:
        return json.loads(out), p
    except:
        return False


def run_direct(args: list[str] or str):
    """
    return Bool
    """
    try:
        p = subprocess.Popen(args)
        p.communicate()
        logging(p, args)
        if p.returncode != 0:
            return False
        else:
            return True
    except:
        return False


def run_with_log(args: list or str):
    """
    PIPE를 통해 실시간으로 결과값을 받습니다.
    """
    cmd_logging(args)
    p = subprocess.Popen(args, stdout=subprocess.PIPE)
    out, err = p.communicate()
    logging(p, args)
    # nbframe과 log의 frame을 합치면 프로그레스바를 표시 할 수 있을 것 같음
    if p.returncode != 0:
        return False
    else:
        return True


def cmd_logging(arg):
    logzero.logfile("live.log",
                    disableStderrLogger=False, encoding="utf-8")
    logger.info("\n" + arg)


def logging(p, args):
    logzero.logfile("live.log",
                    disableStderrLogger=False, encoding="utf-8")
    history = bytearray()
    try:
        for char in iter(lambda: p.stdout.read(1), b''):
            print(char.decode(), end='')
            if char == b'\r':
                char = b'\n'
            history.extend(char)
    except:
        pass
    logged = ""
    if type(args) == list:
        logged = " ".join(args)
    else:
        logged = args
    logger.info("\n" + logged)
    logger.info(history.decode().strip())
    pass
