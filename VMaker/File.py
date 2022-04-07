
from .Settings import Settings
from .commands import run_cmd
from .func import *
import os
import re
import ffmpeg as ff


settings = Settings.get_setting_file_name(os.getcwd())


class File:
    pathes = []
    result_prefix = ""
    origin_prefix = ""
    duration = 0
    idx = 0
    files_list = []

    def __init__(self, p, originpath=settings.origin_path):
        self._file = self.validator(p)
        self.origin_prefix = originpath
        self.pathes.append(self)
        info = self.path_to_ffmpeg()
        self.setffmpeg(info)
        File.files_list.append(self)

    def __call__(self):
        return self._file

    def __str__(self):
        return self._file

    def validator(self, p):
        if os.path.dirname(p):
            raise Exception('파일명만 입력 가능합니다')
        return p

    def setffmpeg(self, attribute: dict):
        for k, v in attribute.items():
            setattr(self, k, v)
            self.is_ffmpeg = True

    @classmethod
    def get_mp4_files(cls, originpath=settings.origin_path):
        """
        이 메소드로 폴더에있는 mp4파일들을 가져옵니다.
        """
        _file_names: list[str] = os.listdir(originpath)
        file_names: list = []
        print(originpath)
        print(os.getcwd())
        for i, _file in enumerate(_file_names):
            if ".mp4" in _file:
                f = cls(_file, originpath)
                f.idx = i
                file_names.append(f)
        file_names.sort()
        if len(file_names) == 0:
            raise Exception("{}에 mp4파일이 없습니다.".format(originpath))
        return file_names

    @classmethod
    def get_highest_bit_rate(cls):
        highest = 0
        for i in File.files_list:
            if i.bit_rate > highest:
                highest = i.bit_rate
        return highest

    def path_to_ffmpeg(self):
        """
        파일 주소를 기반으로 ffmpeg 정보를 반환합니다.
        """
        file = self.origin_full
        args = ['ffprobe', '-show_format',
                '-show_streams', '-of', 'json', file]
        info, p = run_cmd(args)
        try:
            duration: int = int(float(info.get("format").get('duration')))
            bit_rate: int = int(float(info.get("format").get('bit_rate')))
            frame_rate = int(info.get("streams")[0].get(
                'avg_frame_rate').split('/')[0])

            status: dict = {}
            status.update(duration=duration)
            status.update(frame_rate=frame_rate)
            status.update(bit_rate=bit_rate)
            if p.returncode != 0:
                # raise
                pass
            return status
        except:
            raise Exception('유효하지 않은 mp4파일입니다.')

    def remove(self, video, audio, multi_source=True):
        v_t_list = []
        a_t_list = []
        order = self.get_my_options.remove
        cur_order = range_reverser(
            self.duration, order)
        total = 0
        for i in cur_order:
            start, end = range_to_float(i)
            v_t_list.append(
                video.filter('trim', start=start, duration=f_to_s(end-start)).setpts('PTS-STARTPTS'))
            a_t_list.append(
                audio.filter('atrim', start=start, duration=f_to_s(end-start)).filter('asetpts', 'PTS-STARTPTS'))
            total += end-start
        v_o, a_o = merge(v_t_list, a_t_list, multi_source)
        print("감소량", self.duration, total)
        return v_o, a_o, total

    def aremove(self, options, video, audio, multi_source=True):
        aremove = self.get_my_options.aremove
        duration = self.duration
        v_t_list = []
        a_t_list = []
        if 'remove' not in options:
            t = mapper("solo", range_reverser(duration, aremove))
            l = mapper("mute", range_give_zero(duration, aremove))
        else:
            cur_r = aremove_after_remove(range_give_zero(duration, aremove),
                                         range_give_zero(
                                             duration, self.get_my_options.remove)
                                         )
            t = mapper("solo", range_reverser(duration, cur_r))
            l = mapper("mute", range_give_zero(duration, cur_r))
        sum = sorted(t+l, key=lambda x: arm_sort_key(x))
        for i in sum:
            start, end = list(
                map(lambda x: float(x), i[1].split("~")))
            if i[0] == "solo":
                audio = audio.filter(
                    'volume', enable='between(t,{},{})'.format(start, end), volume=1)
            else:
                audio = audio.filter(
                    'volume', enable='between(t,{},{})'.format(start, end), volume=0)
        v_t_list.append(video)
        a_t_list.append(audio)
        v_o, a_o = merge(v_t_list, a_t_list, multi_source)
        return v_o, a_o

    def fadein(self, video, audio):
        duration = self.get_my_options.fadein
        v_t_list = []
        a_t_list = []
        v_t_list.append(
            video.filter('fade', type="in",
                         start_time=0, d=duration)
        )
        a_t_list.append(
            audio.filter('afade', type="in",
                         start_time=0, d=duration)
        )
        video, audio = merge(v_t_list, a_t_list)
        return video, audio

    def fadeout(self, video, audio, length):
        duration = self.get_my_options.fadeout
        print("fadeout", duration, length-duration)
        v_t_list = []
        a_t_list = []
        v_t_list.append(
            video.filter(
                'fade', type="out", start_time=length-duration, d=duration)
        )
        a_t_list.append(
            audio.filter(
                'afade', type="out", start_time=length-duration, d=duration)
        )
        video, audio = merge(v_t_list, a_t_list)
        return video, audio

    @property
    def ffmpeg(self):
        return ff.input(self.origin_full)

    @ property
    def get_my_options(self):  # , options: Options):
        # 3

        for i in settings.options().keys():
            if self.file == i:
                return settings.options().get(i)

    @ property
    def size(self):
        number = int(re.sub(r'[^0-9]', '', self.file))
        return number

    def __lt__(self, other):
        return self.size < other.size

    def __le__(self, other):
        return self.size <= other.size

    def __gt__(self, other):
        return self.size > other.size

    def __ge__(self, other):
        return self.size >= other.size

    def __eq__(self, other):
        return self.size == other.size

    def __eq__(self, other):
        return self.size != other.size

    @ property
    def file(self):
        return self._file

    @ property
    def origin_full(self):
        if self.origin_prefix:
            return f"{self.origin_prefix}/{self.file}"
        else:
            raise Exception("temp경로가 설정되지 않았습니다.")

    @ property
    def temp_full(self):
        if self.origin_prefix:
            return f"{self.origin_prefix}/{self.temp_file}"
        else:
            raise Exception("temp경로가 설정되지 않았습니다.")

    @ property
    def temp_file(self):
        return f"temp_{self.file}"

    @ property
    def result_file(self):
        if self.result_prefix:
            return f"{self.result_prefix}/{self.file}"
        else:
            raise Exception("temp경로가 설정되지 않았습니다.")
