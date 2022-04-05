import ffmpeg
import sys

from . import upload_playlist
from .File import *
from .Settings import *
from .commands import *
from .rm import *
from .func import *
from . import upload_video
settings = Settings.get_setting_file_name('.')


def main(src: list[File] = []):

    v_outputs = []
    a_outputs = []
    for file in src:
        v = file.ffmpeg.video
        a = file.ffmpeg.audio
        frame = file.frame_rate
        if file.get_my_options:
            # 모든구간 페이드인 페이드아웃 처리해야될것같음.
            v_t_list = []
            a_t_list = []
            options = file.get_my_options.keys

            if 'remove' in options:
                print("here")
                order = file.get_my_options.remove
                cur_order = range_reverser(
                    file.duration, order)
                for i in cur_order:
                    start, end = range_to_float(i)
                    v_t_list.append(
                        v.filter('trim', start=start, duration=f_to_s(end-start)).setpts('PTS-STARTPTS'))
                    a_t_list.append(
                        a.filter('atrim', start=start, duration=f_to_s(end-start)).filter('asetpts', 'PTS-STARTPTS'))
                v, a = merge(v_t_list, a_t_list)
                v_t_list = []
                a_t_list = []

            if "aremove" in options:
                print("aremove")
                aremove = file.get_my_options.aremove
                duration = file.duration
                if 'remove' not in options:
                    t = mapper("solo", range_reverser(duration, aremove))
                    l = mapper("mute", range_give_zero(duration, aremove))
                else:
                    cur_r = aremove_after_remove(aremove,
                                                 range_give_zero(
                                                     duration, file.get_my_options.remove)
                                                 )
                    t = mapper("solo", range_reverser(duration, cur_r))
                    l = mapper("mute", range_give_zero(duration, cur_r))
                sum = sorted(t+l, key=lambda x: arm_sort_key(x))
                print(sum)
                for i in sum:
                    start, end = list(
                        map(lambda x: float(x), i[1].split("~")))
                    if i[0] == "solo":
                        a = a.filter(
                            'volume', enable='between(t,{},{})'.format(start, end), volume=1)
                    else:
                        a = a.filter(
                            'volume', enable='between(t,{},{})'.format(start, end), volume=0)
                v_t_list.append(v)
                a_t_list.append(a)
                v, a = merge(v_t_list, a_t_list)
                v_t_list = []
                a_t_list = []
            if 'fadein' in options:
                print("fadein")
                order = file.get_my_options.fadein
                duration = order.duration
                v_t_list.append(
                    v.filter('fade', type="in",
                             start_time=0, d=duration)
                )
                a_t_list.append(
                    a.filter('afade', type="in",
                             start_time=0, d=duration)
                )
                v, a = merge(v_t_list, a_t_list)
                v_t_list = []
                a_t_list = []
            if 'fadeout' in options:
                print("fadeout")
                order = file.get_my_options.fadeout
                duration = order.duration
                v_t_list.append(
                    v.filter(
                        'fade', type="out", start_time=file.duration-duration, d=file.duration)
                )
                a_t_list.append(
                    a.filter(
                        'afade', type="out", start_time=file.duration-duration, d=file.duration)
                )
                v, a = merge(v_t_list, a_t_list)
                v_t_list = []
                a_t_list = []

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
        "o_V"
        output = ffmpeg.output(v_o, a_o, settings.result_full)
        output.run()
        cmd_logging(get_args(output.get_args()))

    if settings.youtube:
        print(settings.youtube)
        _s = settings.youtube
        title = _s.get("title") or "Video"
        description = _s.get("description") or ""
        keywords = _s.get("keywords") or ""
        category = _s.get("category") or ""
        privacyStatus = _s.get("privacyStatus") or "private"
        youtube_cmd = f'python upload_video.py --file="{settings.result_full}"  --title="{title}" --description="{description}"  --keywords="{keywords}" --category="{category}" --privacyStatus="{privacyStatus}"'
        cmd_logging(youtube_cmd)
        video_id = upload_video.main(settings.result_full, title,
                                     description, category, keywords, privacyStatus)
        if video_id and settings.playlist.get("playlist"):
            pl_id = settings.playlist.get("playlist")
            upload_playlist.main(pl_id, video_id)
