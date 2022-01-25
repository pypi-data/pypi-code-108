import sys
import importlib
def main():
    command_dict = {
        'md5':         'yxspkg.md5 /help: 计算文件md5值',
        'fafa-excel':  'yxspkg.fafa_excel /help: 自动处理合并excel表格',
        'songzigif':   'yxspkg.songzgif.gif /help: 动图处理软件',
        'songziviewer':'yxspkg.songziviewer /help: 一个简单的图片查看器',
        'm3u8':        'yxspkg.m3u8 /help: 把m3u8文件合并为mp4',
        'server':      'yxspkg.file_server.server /help: 一个简易服务器',
        'video2html':  'yxspkg.video2html /help: 给视频制作html目录',
        'getdata':     'yxspkg.getdata.getdata_qt /help: 图片数据提取软件',
        'convert_url': 'yxspkg.convert_url /help:',
        'image':       'yxspkg.image.image_operator /help:',
        'video':       'yxspkg.video.video_operator /help: 视频处理工具',
        'samefile':    'yxspkg.same_file /help: 检查相同文件',
        'ls':          'yxspkg.yxsfile /help: 简单加密文件和文件名',
        'loop':        'yxspkg.loop_cmd /help: 重复执行命令',
        'xget':        'yxspkg.xget /help: xget',
        'crawl_data':  'yxspkg.Crawl_data /help: 自动爬取数据',
        'wallpaper':   'yxspkg.wallpaper /help: 自动设置屏幕壁纸',
        'gantt':       'yxspkg.Gantt /help: 绘制甘特图',
        'wait_login':  'yxspkg.wait_login /help: 等待linux系统成功登录，主要是为了开机启动任务开发的工具'
    }
    run_yxs_command(sys.argv,command_dict)
def run_yxs_command(argv,command_dict):
    if len(argv) > 1:
        cmd = argv[1]
        argv.pop(1)
        sys.argv = argv
    else:
        cmd = '--help'
    if cmd not in command_dict:
        cmd = '--help'
    if cmd == '--help':
        print('useage:module list')
        l = list(command_dict.keys())
        l.sort(key=lambda x:x.lower())
        max_length = max([len(i) for i in l])+4
        fmt = '    {:max_lengths}'.replace('max_length',str(max_length))
        for i in l:
            tcmd = command_dict[i]
            if tcmd.find('/help:') != -1:
                help_info = command_dict[i].split('/help:')[1].strip()
            else:
                help_info = ''
            print(fmt.format(i),end='')
            print(help_info)
    else:
        tcmd = command_dict[cmd].split('/help:')[0].strip()
        importlib.import_module(tcmd).main()
if __name__=='__main__':
    main()