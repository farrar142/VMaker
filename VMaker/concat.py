import ffmpeg
import sys

# from . import upload_playlist
# from . import upload_video
from .Settings import *
from .commands import *
from .rm import *
from .func import *
settings = Settings.get_setting_file_name('.')


def main(src=[]):
    multi_source = True if len(src) > 1 else False
    v_outputs = []
    a_outputs = []
    for file in src:
        v = file.ffmpeg.video
        a = file.ffmpeg.audio
        frame = file.frame_rate
        duration = file.duration
        if file.get_my_options:
            # 모든구간 페이드인 페이드아웃 처리해야될것같음.
            v_t_list = []
            a_t_list = []
            options = file.get_my_options.keys

            if 'remove' in options:
                v, a, duration = file.remove(v, a, multi_source)
            if "aremove" in options:
                v, a = file.aremove(options, v, a, multi_source)
            if 'fadein' in options:
                v, a = file.fadein(v, a)
            if 'fadeout' in options:
                v, a = file.fadeout(v, a, duration)

        v_outputs.append(v)
        a_outputs.append(a)
    if not settings.files:
        temp = "./temp"

        def cmd_can(file):
            return f'ffmpeg -y -i "{file.origin_full}" -c copy -f mpegts {temp}/t{file.idx}.ts', f"{temp}/t{file.idx}.ts"
        mylist = [cmd_can(file)[0] for file in src]
        outputs = [cmd_can(file)[1] for file in src]
        force_mkdir(settings.result_path)
        force_mkdir(temp)
        [run_with_log(cmd) for cmd in mylist]
        _concat = f'ffmpeg -y -i "concat:{"|".join(outputs)}" -c copy {settings.result_full}'
        run_with_log(_concat)
        force_rmdir(temp)

    else:
        v_o, a_o = merge(v_outputs, a_outputs)
        if settings.find("resolution"):
            res = settings.get("resolution")
            v_o = v_o.filter(
                res.get('filter_name'), size=res.get("size"))
        force_mkdir(settings.result_path)
        output = ffmpeg.output(
            v_o, a_o, settings.result_full, b=src[0].get_highest_bit_rate(), vcodec='libx264', crf=0)
        output.run()
        cmd_logging(get_args(output.get_args()))

    # if settings.youtube:
    #     print(settings.youtube)
    #     _s = settings.youtube
    #     title = _s.get("title") or "Video"
    #     description = _s.get("description") or ""
    #     keywords = _s.get("keywords") or ""
    #     category = _s.get("category") or ""
    #     privacyStatus = _s.get("privacyStatus") or "private"
    #     youtube_cmd = f'python upload_video.py --file="{settings.result_full}"  --title="{title}" --description="{description}"  --keywords="{keywords}" --category="{category}" --privacyStatus="{privacyStatus}"'
    #     cmd_logging(youtube_cmd)
    #     video_id = upload_video.main(settings.result_full, title,
    #                                  description, category, keywords, privacyStatus)
    #     if video_id and settings.playlist.get("playlist"):
    #         pl_id = settings.playlist.get("playlist")
    #         upload_playlist.main(pl_id, video_id)
