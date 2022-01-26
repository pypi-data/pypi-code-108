import subprocess 
import click 
import time
from pathlib import Path

@click.command(help='自动多次重复执行命令')
@click.argument('commands',nargs=1)
@click.option('--max_iter','-m',default=1,help='最大重复同步次数')
@click.option('--interval','-i',default=120,help="间隔时间,默认120秒")
@click.option('--success','-s',default=False,help="执行命令直到成功执行一次为止")
def main(commands,max_iter,interval,success):
    ii = 0
    while True:
        ii += 1
        if Path('stop_loop').exists():
            break 
        else:
            print('no file stop_loop to stop it')
        try:
            subprocess.check_call(commands,shell=True)
            if success:
                break
        except Exception as e:
            print(e)
        if interval > 0:
            print(f'sleep {interval}s')
            time.sleep(interval)
        if max_iter>0 and ii>=max_iter:
            break
    print(f'run commands for {ii} times')
if __name__=='__main__':
    main()