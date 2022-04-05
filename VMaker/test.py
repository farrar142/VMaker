
from VMaker import concat
import json
import os
import unittest
from VMaker.File import File
from VMaker.Settings import Settings
import ffmpeg
from pprint import pprint
from pathlib import Path as p
slow = not True


class TestVMaker(unittest.TestCase):
    def eq(self, p, v):
        return self.assertEqual(p, v)

    def ne(self, p, v):
        return self.assertNotEqual(p, v)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.vmaker = VMaker()

    def test_vmaker_init(self):
        vm = self.vmaker
        s_file = open("./settings.json", 'r', encoding="utf-8")
        setting_file: dict = json.loads(
            s_file.read())
        s_file.close()
        # VMaker 초기화 테스ㅌ,
        self.assertEqual(vm.cur_path, os.getcwd())
        # 세팅파일 위치 가져오기.
        self.assertEqual(vm.params.settings_path,
                         Settings.get_setting_file_name(os.getcwd()).settings_path)
        # 제대로 가져왔는지 확인
        self.assertEqual(vm.params.test, setting_file["test"])
        self.assertNotEqual(vm.params.test, setting_file["test2"])
        # temp 폴더에 가있는지 확인
        self.assertEqual(os.path.isfile(vm.temp_path+'/01.mp4'), True)
        # 1.초기정보를 세팅함.
        # 2.temp폴더로 옮김.

    def test_vmaker_concat_test(self):
        vm = self.vmaker
        if slow:
            # concat으로 반환된 영상의 길이와 concat된 후의 영상 길이가 같음.
            result: File = vm.concat()
            check_result: File = File.get_mp4_files(vm.result_path)[0]
            self.eq(result.duration, check_result.duration)
        origin_files = File.get_mp4_files(vm.origin_path)
        temp = File.get_mp4_files(vm.temp_path)[0]
        vm.run()
        result = File.get_mp4_files(vm.result_path)[0]
        check_result: list(File) = File.get_mp4_files(vm.temp_path)
        # remove를 하기 전의 파일보다 remove한 후의 파일의 길이가 적음.
        self.assertGreater(temp.duration, result.duration)
        # remove한 후, Concat전의 파일들의 크기와 Concat후의 파일 크기가 같음.
        self.eq(result.duration, sum(map(lambda x: x.duration, check_result)))
        self.assertLess(result.duration, sum(
            map(lambda x: x.duration, origin_files)))


class TestFile(unittest.TestCase):
    def eq(self, p, v):
        return self.assertEqual(p, v)

    def ne(self, p, v):
        return self.assertNotEqual(p, v)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def test_path_init(self):
        # 오리진 폴더의 파일들
        of: list[File] = File.get_mp4_files('./origin')
        self.eq(of[0].origin_prefix, of[1].origin_prefix)

        of[1].origin_prefix = "notorigin"
        self.ne(of[0].origin_prefix, of[1].origin_prefix)

        # 템프 폴더의 파일들
        tf: list[File] = File.get_mp4_files('./temp')
        # 과 기존 파일들은 근본이 다름.
        self.ne(of[0].origin_prefix, tf[0].origin_prefix)
        # 비교 메서드 확인
        self.assertLess(of[0], of[1])


if __name__ == "__main__":
    unittest.main()
