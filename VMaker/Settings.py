import json
import os
import platform

sep = "\\" if platform.system() == "Windows" else "/"


class setting:
    def find(self, attr):
        for i in self().keys():
            if attr == i:
                return True

        return False

    def get(self, attr):
        for i in self().keys():
            if attr == i:
                return self().get(attr)
        return None

    def __call__(self):
        return self.__dict__

    @property
    def dict(self):
        return self.__dict__

    @property
    def keys(self):
        return self.__dict__.keys()

    @property
    def items(self):
        return self.__dict__.items()

    def __getattr__(self, __name: str):
        return None

    def __setattr__(self, __name: str, __value):
        if __name in self.keys:
            return False
        super().__setattr__(__name, __value)


class Settings(setting):
    origin_path = ""
    result_path = ""
    result_file = ""
    resolution = {}
    fadein = 0
    fadeout = 0

    def __init__(self, path):
        self.settings_path = path
        self.settings: dict = self.json_parser()
        self.setAttr(self.settings)
        self.origin_path = self.settings.get("filesPath") or "."
        self.result_path = self.settings.get("resultPath") or "./result"
        self.result_file = self.settings.get("resultFile") or "result.mp4"
        self.options = Options(self.settings.get("files") or {})

    @property
    def result_full(self):
        return f"{self.result_path}/{self.result_file}"

    def setAttr(self, attribute: dict):
        for k, v in attribute.items():
            setattr(self, k, v)

    @classmethod
    def get_setting_file_name(cls, path=os.getcwd(), setting_file_name: str = "settings.json"):
        path: str = path+sep+setting_file_name
        if os.path.isfile(path):
            print("{}의 settings.json 파일을 사용합니다.".format(path))
            return cls(path)
        else:
            print("{}에 settings.json파일을 찾을 수 없습니다. 기본 설정을 이용합니다.".format(path))
            return cls(path)

    def json_parser(self):
        try:
            targetfile = open(
                self.settings_path, "r", encoding="utf-8")
            result = targetfile.read()
            targetfile.close()
            return json.loads(result)
        except:
            return {'filesPath': ".", 'resultPath': './result', 'resultFile': 'result.mp4'}


class Options(setting):
    def __init__(self, attr):
        for k, v in attr.items():
            if type(v) == dict:
                setattr(self, k, Options(v))
            else:
                setattr(self, k, v)
