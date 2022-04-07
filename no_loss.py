import ffmpeg
from VMaker.File import File
files: list[File] = File.get_mp4_files
file = files[0].ffmpeg

v = file.video
a = file.audio
a = a.filter('volume', enable='between(t,0,30)', volume=0)
result = ffmpeg.output(v, a, 'result.mp4', acodec='copy', vcodec='copy')
print(result.run())
