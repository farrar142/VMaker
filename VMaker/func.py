
import itertools
import re
from pathlib import Path as p
import ffmpeg
import sys
import platform
import os

sys.path.append(str(p(__file__).parent.parent))
if True:
    from VMaker.Settings import Settings
sep = "\\" if platform.system() == "Windows" else "/"

settings = Settings.get_setting_file_name(os.getcwd())


def get_after_file_len(args):
    r = (list(map(lambda x: s_f(x), args)))
    return str(sum(r))


def resolution_cmd(temp_path, file):
    """
    >>> resolution_cmd('./temp','01.mp4')
    'ffmpeg -i ./temp/01.mp4 -vf "scale=480:320" -c:a copy ./temp/temp_01.mp4'
    """
    opt = ""
    if settings.resolution:
        opt = optionParser(**settings.resolution)

    result = f"ffmpeg -i {temp_path}/{file} -vf \"{opt}\" -c:a copy {temp_path}/temp_{file}"
    return result


def trim_cmd(temp_path, file, command):
    """
    >>> trim_cmd('./temp','01.mp4','')
    'ffmpeg -i ./temp/01.mp4 -vf "select=\\'\\', setpts=N/FRAME_RATE/TB" -af "aselect=\\'\\', asetpts=N/SR/TB" ./temp/temp_01.mp4'
    """
    result = f"ffmpeg -i {temp_path}/{file} -vf \"select='{command}', setpts=N/FRAME_RATE/TB\" -af \"aselect='{command}', asetpts=N/SR/TB\" {temp_path}/temp_{file}"
    return result


def fade_cmd(temp_path, file, duration):
    """
    >>> fade_cmd('./temp','01.mp4','600')
    'ffmpeg -i ./temp/01.mp4 -vf "fade=t=in:st=0:d=3,fade=t=out:st=596:d=3" -af "afade=t=in:st=0:d=3,afade=t=out:st=596:d=3"  ./temp/temp_01.mp4'
    """
    voptions = []
    aoptions = []
    fadein = ""
    if settings.fadein:
        i = str(settings.fadein.get("duration"))
        fadein = f"fade=t=in:st=0:d={i}"
        voptions.append(fadein)
        aoptions.append("a"+fadein)
    fadeout = ""
    o = "0"
    if settings.fadeout:
        o = str(settings.fadeout.get("duration"))
        fadeout = f"fade=t=out:st={f_s(duration,-float(o))}:d={o}"
        voptions.append(fadeout)
        aoptions.append("a"+fadeout)
    # fadeout은 trim단계에서 duration과 잘라낸구간의 합을 빼서 구해야될것같음.
    voptions = ','.join([i for i in voptions if i != ""])
    aoptions = ','.join([i for i in aoptions if i != ""])
    result = f"ffmpeg -i {temp_path}/{file} -vf \"{voptions}\" -af \"{aoptions}\"  {temp_path}/temp_{file}"
    return result

# temp


def aremove_after_remove(a, r):
    a_offset = [[0, 0, 0] for i in a]
    reduction = 0
    for remove in r:
        remove_start, remove_end = range_to_float(remove)
        x_reduction = reduction
        cur_reduction = remove_end - remove_start
        reduction += cur_reduction
        for arm_index, arm in enumerate(a):
            offset = a_offset[arm_index]
            arm_start, arm_end = range_to_float(arm)
            # start offset
            if remove_start < arm_start and remove_end > arm_end:
                offset = [-arm_start, -arm_end, 0]
            elif remove_end < arm_start or remove_start > arm_end:
                if arm_start > remove_end:
                    offset = offset
                else:
                    continue
            elif remove_start >= arm_start or remove_end <= arm_end:
                # arm start는 영향이 없을때
                if remove_start > arm_start:
                    # remove_end 가 arm_end보다 작을때
                    if remove_end < arm_end:
                        # 삭제된 이후로도 뮤트음이 남아있으므로 수정
                        offset[0] += remove_end-remove_start
                    # remove_end가 arm_end보다 같거나 클때
                    elif remove_end >= arm_end:
                        offset[0] += cur_reduction
                        offset[1] += cur_reduction+remove_start-arm_end
                if remove_start <= arm_start:
                    offset[0] += remove_end - arm_start
            offset[2] = reduction
            a_offset[arm_index] = offset

    return list_to_cmd(offsetter(cmd_to_list(a), a_offset))


def range_give_zero(duration: str, command: list):
    res = []
    is_start = False
    is_end = False
    start = command[0].split("~")

    if start[0] == "":
        command[0] = f"0~{start[1]}"
        is_start = True
    if len(command) >= 2:
        end = command[-1].split("~")
        if end[0] == "":
            command[-1] = f"{float(duration)-float(end[1])}~{duration}"
    print(command)
    return command


def range_reverser(duration: str, command: list):
    """
    >>> range_reverser(200,['~3','5~10','20~30'])
    ['3~5', '10~20', '30~200']
    >>> range_reverser(250,['5~10','20~30','~30'])
    ['0~5', '10~20', '30~220']
    >>> range_reverser(300,['5~10','20~30'])
    ['0~5', '10~20', '30~300']
    """
    start = False
    end = False
    try:
        _t = command[0].split("~")
        if _t[0] == "" and _t[1]:
            start = True
    except:
        pass
    try:
        _t = command[-1].split("~")
        if len(command) >= 2 and _t[0] == "" and _t[1]:
            end = True
    except:
        pass
    command_list = list(map(lambda x: x.split("~"), command))
    tmp_list = list(itertools.chain(*command_list))
    tmp_list = [i for i in tmp_list if i]

    command_list = " ".join(tmp_list).split(" ")
    if not start:
        command_list = ['0'] + command_list
    if not end:
        command_list += [duration]
    else:
        command_list[-1] = str(int(duration)-int(_t[1]))
    tmp_list = []
    for i in range(len(command_list)):
        if i % 2 == 0:
            tmp_list.append(f"{command_list[i]}~{command_list[i+1]}")
    return tmp_list
# https://superuser.com/questions/681885/how-trim_cmd-i-remove-multiple-segments-from-a-video-using-ffmpeg
# ffmpeg -i input.avi -vf "select='lt(t,20)+between(t,790,810)+gt(t,1440)',setpts=N/FRAME_RATE/TB" -af
# "aselect='lt(t,20)+between(t,790,810)+gt(t,1440)', asetpts=N/SR/TB" output.avi
# remove functions starts


def optionParser(**kwargs):
    result = []
    for k, v in kwargs.items():
        result.append(f"{k}={v}")
    result = f'{",".join(result)}'
    if not result:
        return ""
    else:
        return result


def d_to_int(file: dict):
    return int(float(file.get("status").get("duration")))


def s_k(cmd: str):
    return float(cmd.split("~")[0] or 0)


def bVk(cmd: str):
    c = cmd.split("~")
    f = float(c[0])
    p = float(c[1])
    if (f > p):
        raise Exception(f"중간값{f}가 {p} 보다 큽니다.")
# remove functions ends

# remove validator starts


def end_trimmer_validator(val1: int, val2: int):
    pass


def remove_command_input_validator(remove_command: list):
    """
    >>> remove_command_input_validator(['~3','5~10','20~30'])
    >>> remove_command_input_validator(['~3','510','20~30'])
    Traceback (most recent call last):
    Exception: remove 명령어엔 ~가 포함되어야합니다.
    """

    def inner(val: str):
        if not val.count("~"):
            raise Exception("remove 명령어엔 ~가 포함되어야합니다.")
    try:
        list(map(lambda x: inner(x), remove_command))
    except:
        raise


def between_validator(remove_command: list):
    # print("remove_command : ", remove_command)
    list(map(lambda x: bVk(x), remove_command))
    pass
# remove validator ends

# remove trimmer starts


def trimmer(command: list, option: list):
    """
    >>> trimmer([],['5~10','20~30'])
    (['between(t,5,10)', 'between(t,20,30)'], [])
    """
    between = option[0].split("~")
    if between[0] != "" and between[1] != "":
        command.append(f"between(t,{between[0]},{between[1]})")
        option.pop(0)

    if len(option) >= 1 and option[0].split("~")[0] != "":
        # 엔드라인이 아닐경우
        trimmer(command, option)
    # 스택에서 나갈때.
    return command, option


def side_trimmer(option: list[str]):
    """
    >>> side_trimmer(['0~3','5~10','20~30'])
    'between(t,0,3)+between(t,5,10)+between(t,20,30)'
    >>> side_trimmer(['5~10','20~30','30~230'])
    'between(t,5,10)+between(t,20,30)+between(t,30,230)'
    >>> side_trimmer(['0~5','20~50','200~300','400~1000'])
    'between(t,0,5)+between(t,20,50)+between(t,200,300)+between(t,400,1000)'
    """
    command: list = []
    betweens: list = []
    option.sort(key=lambda v: s_k(v))
    between_validator(option)
    # 중간 trim() 명령어 파싱
    betweens, option = trimmer(betweens, option)
    command += betweens
    result: str = "+".join(command)
    return result
# remove trimmer ends


def str_to_float(t: str):
    if not t:
        return 0
    return float(re.sub(r'[^0-9]', '', t))


def f_s(a, b):
    res = str(int(float(a)+float(b))-1)
    return res


def s_f(arg: str):
    """
    str to float
    """
    a, b = arg.split("~")

    return float(b)-float(a)


if __name__ == "__main__":
    import doctest
    doctest.testmod()


def f_to_s(num: float):
    return f"{num:.2f}"


def list_zipper(a, b):
    j_t_l = list(zip(a, b))
    _j_t_l = []
    for i in j_t_l:
        _j_t_l.append(i[0])
        _j_t_l.append(i[1])
    return _j_t_l


def cmd_to_list(cmd):
    return list(map(lambda x: [range_to_float(x)[0], range_to_float(x)[1]], cmd))


def offsetter(a, b):
    res = []
    for x, y in zip(a, b):
        t_res = [0, 0]
        t_res[0] = x[0]+y[0]-y[2]
        t_res[1] = x[1]+y[1]-y[2]
        res.append(t_res)
    return res


def list_to_cmd(a):
    return list(map(lambda x: f'{x[0]:.2f}~{x[1]:.2f}', a))


def mapper(keywords, arr):
    return list(map(lambda x: (keywords, x), arr))


def arm_sort_key(target):
    return float(target[1].split("~")[0])


def merge(a, b, multi_source=True, output=False):
    joined = ffmpeg.concat(*list_zipper(a, b), v=1,
                           a=1).node
    a, b = [], []
    return joined[0], joined[1]


def get_args(args):
    res = "ffmpeg -y "+" ".join(args)
    res = [i for i in res if i != '\\']
    return "".join(res)


def range_to_float(t: str):
    a, b = t.split("~")
    # a = f"{float(a):.2f}"
    # b = f"{float(a):.2f}"
    return float(a), float(b)


"""
ffmpeg -y -i 01.mp4 -filter_complex
"""
