import sys 
import os
from pathlib import Path
import hashlib
import shutil
import click
from yxspkg import yxsfile
def get_md5(fname):
    # fp = open(fname,'rb')
    # md5 = hashlib.md5()
    # while True:
    #     t = fp.read(1024*1024*4)
    #     if t == b'':
    #         break
    #     md5.update(t)
    # return md5
    return yxsfile.yxsFile(fname).get_md5()
def issame(file1,file2):
    # size1 = file1.stat().st_size
    # size2 = file2.stat().st_size
    # if size1 != size2:
    #     return False
    md51 = get_md5(file1).hexdigest()
    md52 = get_md5(file2).hexdigest()
    if md51 == md52:
        return True 
    else:
        return False
    

def find_all_pics(p,suffix,picdir=None,video_suffix='.mp4'):
    suffix = '*'+suffix
    result =[]
    for root,dirs,files in os.walk(p):
        right_dir = False
        proot = Path(root).absolute()
        root_name = proot.name
        if picdir:
            if root_name==picdir:
                right_dir = True
        else:
            right_dir = True
        if right_dir:
            for fname in proot.glob(suffix):
                if fname.is_file() and not fname.is_symlink():
                    mp4_file = fname.parent.parent / fname.with_suffix(video_suffix).name 
                    if mp4_file.is_file() and not fname.is_symlink():
                        result.append([fname,fname.stat().st_size,mp4_file])
    return result
def delete_first(file1,file2):
    name1 = file1.name 
    name2 = file2.name 
    tags1 = name1.count('[')
    tags2 = name2.count('[')
    dots1 = name1.count('.')
    dots2 = name2.count('.')
    if tags1 != tags2:
        if tags1 < tags2:
            is_first = True
        else:
            is_first = False 
    elif dots1 != dots2:
        if dots1 < dots2:
            is_first = True 
        else: 
            is_first = False
    else:
        is_first = True 
    if is_first:
        if file1.stat().st_size > file2.stat().st_size:
            temp_file = file2.with_name('__teemp__file__')
            os.rename(file1,temp_file)
            os.rename(file2,file1)
            os.rename(temp_file,file2) 
    return is_first
def get_file_suffix(inputdir,picdir):
    jpg_suffix,video_suffix = None,None
    for root,_,fs in os.walk(inputdir):
        if Path(root).name == picdir:
            for i in fs:
                if Path(i).suffix == '.jpg':
                    jpg_suffix = '.jpg'
                    video_suffix = '.mp4'
                if Path(i).suffix == '.jpxs':
                    jpg_suffix = '.jpxs'
                    video_suffix = '.mpxs'
    return jpg_suffix,video_suffix
def movefile2trash(filename,trashname):
    if filename.suffix == '.jpxs':
        yxsfile.yxsFile(filename).to_pureFile(trashname)
    else: 
        shutil.move(str(filename),str(trashname))
@click.command()
@click.argument('args',nargs=-1)
@click.option('--not_default',default=False,is_flag=True,help='不采用默认模式')
@click.option('--inputdir','-i',default=None,help='目录名称')
@click.option('--suffix','-s',default=None,help='文件类型设置')
@click.option('--picdir',default=None,help='包含suffix的文件夹名称')
def main(args,inputdir,suffix=None,picdir=None,not_default=False):
    if not not_default:
        picdir = "generate_poster_dir"
        suffix = '.jpg'
    if inputdir is None: 
        inputdir = args[0]
    jpg_suffix,video_suffix = get_file_suffix(inputdir,picdir)
    if not jpg_suffix:
        print('没有发现有用文件')
        return
    if jpg_suffix == '.jpg':
        is_pureFile = True 
    else:
        is_pureFile = False
    result = find_all_pics(inputdir,jpg_suffix,picdir,video_suffix)
    result.sort(key=lambda x:x[1])
    ii = 1
    delete_files = []
    length_result = len(result)
    if len(result) > 1:
        while True:
            if result[ii][1] == result[ii-1][1]:
                if issame(result[ii][0],result[ii-1][0]):
                    delete_files.append([result[ii],result[ii-1]])
                    ii+=1
            ii+=1
            if length_result <= ii:
                break
    if len(delete_files) > 0:
        trash_dir = Path(inputdir).absolute().parent / 'trash_dir'
        if not trash_dir.exists():
            os.mkdir(trash_dir)
        for i in delete_files:
            is_first = delete_first(i[0][2],i[1][2])
            if is_first:
                del_id = 0 
            else:
                del_id = 1
            save_id = 1 - del_id
            print(i[del_id][2],i[del_id][1])
            print(i[save_id][2],i[save_id][1],'\n')
            # shutil.move(str(i[del_id][0]),str(trash_dir))
            # shutil.move(str(i[del_id][2]),str(trash_dir))
            movefile2trash(i[del_id][0],trash_dir)
            movefile2trash(i[del_id][2],trash_dir)
            temp = (trash_dir/i[save_id][0].name)
            if temp.exists():
                temp.unlink()
            temp.symlink_to(i[save_id][0])
if __name__ == '__main__':
    os.chdir('/home/yxs/Documents/pythonAPP/yxsfile')
    sys.argv.append('./video')
    main()