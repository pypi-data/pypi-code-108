import os
import subprocess
import click 
from pathlib import Path
import subprocess
import json
import time

@click.command()
@click.argument('args',nargs=-1)
@click.option('--rotate',default=None,help='旋转视频')
@click.option('--replace',default=False,help='是否替换该文件',is_flag=True)
@click.option('--ffmpeg_parameter','-f',default='-c copy',help='ffmpeg 参数')
@click.option('--to_mp4',default=False,help='将文件转化为mp4格式',is_flag=True)
@click.option('--delete',default=False,help='删除源文件',is_flag=True)
def main(args,replace,rotate,ffmpeg_parameter,to_mp4,delete):
    if to_mp4:
        convert2mp4(args,delete)
        return 
    input_file = Path(args[0]).absolute()
    if len(args) > 1:
        output_file = Path(args[1]).absolute()
    else:
        output_file = input_file.parent / (input_file.stem+'_output'+input_file.suffix)
    temp_file = output_file.parent / (output_file.stem+'_temp'+output_file.suffix)
    ffmpeg_i = f'ffmpeg -i "{input_file}" '
    if rotate:
        ffmpeg_command = ffmpeg_i + f' -metadata:s:v:0 rotate={rotate} ' + ffmpeg_parameter +f' "{temp_file}"'
    t = subprocess.call(ffmpeg_command,shell=True)
    assert t == 0
    if replace:
        os.rename(temp_file,input_file)
    else:
        os.rename(temp_file,output_file)
def convert2mp4(args,delete=False):
    other_video = {'.avi','.mkv','.rmvb','.wmv','.mpg','.mov','.rm','.flv','3gp','.asf','.mod','.rmvb'}
    if len(args) > 0:
        pnw = Path(args[0])
    else:
        pnw = Path('./')
    for root,_,fs in os.walk(pnw):
        for f in fs:
            if Path(f).suffix.lower() in other_video:
                vfile = Path(root) / f
                params = get_video_parameter(vfile)
                code_names = set([i['codec_name'] for i in params['streams']])
                if 'aac' in code_names:
                    codea = 'copy'
                else:
                    codea = 'aac'
                if 'h264' in code_names or 'libx264' in code_names:
                    codev = 'copy'
                else:
                    codev = 'h264'
                mp4file = vfile.with_suffix('.mp4')
                subprocess.call(f'ffmpeg -i "{vfile}" -c:v {codev} -c:a {codea} -y "{mp4file}"',shell=True)
                if delete:
                    time.sleep(0.1)
                    os.remove(vfile)
def get_video_parameter(video_path):
    def filter_parameter(params):
        pl = [i for i in params.splitlines() if not i.startswith('Cannot')]
        return '\n'.join(pl)
    t = f'ffprobe -i "{str(video_path)}" -print_format json -show_format -show_streams -v quiet'
    all_parameter=subprocess.getoutput(t)
    all_parameter = filter_parameter(all_parameter)
    all_parameter=json.loads(all_parameter)
    return all_parameter

# '''
#     get parameter from ffmpeg

#     function    check_ffmepg_exist
#     function    return_all_parameter
#     function    return_video_height_wigth
#     function    return_video_filesize
#     function    return_video_full_frame
#     function    return_video_time_length

# '''
# import os
# import subprocess
# import json
# class ffprboe_parameter():

#     def __init__(self,vdieo_path,env=0):
#         '''
#             env 1 代表使用本地环境变量
#             env 2 代表使用bin目录下的

#         :param env:
#         '''
#         self.check_ffmepg_exist() if env == 1 else print(end='')
#         self.all_parameter = self.return_all_parameter()

#     def check_ffmepg_exist(self):
#         base_dir = os.getcwd() + os.sep + 'bin'
#         assert os.path.exists(base_dir + os.sep + 'ffmpeg.exe'), FileNotFoundError('The bin dir not have ffmpeg.exe')
#         assert os.path.exists(base_dir + os.sep + 'ffprobe.exe'), FileNotFoundError('The bin dir not have ffprobe.exe')
#     @staticmethod
#     def filter_parameter(params):
#         pl = [i for i in params.splitlines() if not i.startswith('Cannot')]
#         return '\n'.join(pl)
#     def return_all_parameter(self,video_path=None):
#         video_path=self.video_path_check(video_path=video_path)
#         assert os.path.exists(video_path),FileNotFoundError('video not found')
#         assert os.path.isfile(video_path),FileExistsError('video is not file,please check it ')
#         try:
#             t = ' '.join(['ffprobe','-i',video_path,'-print_format','json','-show_format','-show_streams','-v','quiet'])
#             all_parameter=subprocess.getoutput(t)
#             all_parameter = self.filter_parameter(all_parameter)
#             print(all_parameter)
#             all_parameter=json.loads(all_parameter)
#         except Exception as e:
#             print(e)
#             raise Exception('error for get video info')
#         return all_parameter

#     def return_video_height_wigth(self,video_path=None):
#         video_path = self.video_path_check(video_path=video_path)
#         tmp=self.return_all_parameter(video_path=video_path)['streams'][0]
#         return (tmp['width'],tmp['height'])

#     def return_video_filesize(self,format='GB',video_path=None):
#         video_path = self.video_path_check(video_path=video_path)
#         tmp = self.return_all_parameter(video_path=video_path)['format']
#         if format.lower()=='gb':
#             return float('%.4f'%(int(tmp['size'])/1024/1024/1024)),format.upper()
#         if format.lower()=='mb':
#             return float('%.4f'%(int(tmp['size'])/1024/1024)),format.upper()
#         if format.lower()=='kb':
#             return float('%.4f' % (int(tmp['size']) / 1024 )), format.upper()


#     def return_video_full_frame(self,video_path=None):
#         video_path=self.video_path_check(video_path=video_path)
#         tmp = self.return_all_parameter(video_path=video_path)['streams'][0]
#         return tmp['nb_frames']

#     def init_video_path(self,video_path):
#         self.video_path=video_path
#         return self.video_path


#     def video_path_check(self,video_path):
#         if video_path == None:
#             try:
#                 video_path=self.video_path
#             except:
#                 raise BaseException('video_path is not define ')
#         return video_path

#     def return_video_time_length(self,video_path=None):
#         video_path=self.video_path_check(video_path=video_path)
#         tmp = self.return_all_parameter(video_path=video_path)['format']
#         return str(int(float(tmp['duration'])/3600)).__add__('小时').__add__(str(int(float(tmp['duration'])%3600/60))).__add__('分钟')




#     def return_all_items(self,video_path=None):
#         video_path=self.video_path_check(video_path=video_path)
#         tmp={
#             'video_height_wigth':list(self.return_video_height_wigth()),
#             'video_filesize':''.join([''.join(str(x)) for x in self.return_video_filesize()]),
#             'video_full_frame':self.return_video_full_frame(),
#             'video_time_length':self.return_video_time_length()
#         }
#         return tmp


if __name__=='__main__':
    # main()
    convert2mp4(['/media/yxs/Blackso/mpxs/tttavi'])
    # t = get_video_parameter(video_path='/media/yxs/Blackso/mpxs/tttavi/HODV-21060.mkv')
    # print(t)