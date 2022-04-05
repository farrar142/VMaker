
from .Settings import Settings
from .commands import run_cmd
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

    def __init__(self, p, originpath=settings.origin_path):
        self._file = self.validator(p)
        self.origin_prefix = originpath
        self.pathes.append(self)
        info = self.path_to_ffmpeg()
        self.setffmpeg(info)

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

    def path_to_ffmpeg(self):
        """
        파일 주소를 기반으로 ffmpeg 정보를 반환합니다.
        """
        file = self.origin_full
        print(file)
        args = ['ffprobe', '-show_format',
                '-show_streams', '-of', 'json', file]
        info, p = run_cmd(args)
        try:
            duration: int = int(float(info.get("format").get('duration')))
            frame_rate = int(info.get("streams")[0].get(
                'avg_frame_rate').split('/')[0])

            status: dict = {}
            status.update(duration=duration)
            status.update(frame_rate=frame_rate)
            if p.returncode != 0:
                # raise
                pass
            return status
        except:
            raise Exception('유효하지 않은 mp4파일입니다.')

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
