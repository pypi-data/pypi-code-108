
import os


def os_system(cmd):
    try:
        n = os.system(cmd) >> 8
        if n != 0:
            print('shell执行失败：%d %s' % (n, cmd))
            raise Exception(cmd)
    except Exception as e:
        raise e


def os_popen(cmd):
    try:
        cmd = (cmd + '; if [ $? -ne 0 ]; then echo "{{error}}"; fi').replace(';;',';')
        with os.popen(cmd) as p:
            output = p.read()
            if '{{error}}' in output:
                output = output.replace('{{error}}','')
                cmd = cmd.replace('if [ $? -ne 0 ]; then echo "{{error}}"; fi', '')
                err = '命令执行失败：%s output=%s' % (cmd, output)
                print(err)
                return (False, err)
            else:
                return (True, 'success')
    except Exception as e:
        raise e


#  ShellCMD.py 执行shell脚本的工具类
if __name__ == '__main__':
    # os_system('cat aaa')
    (status, msg) = os_popen('xcodebuild  aaa > /dev/null')
    print(status)
    print(msg)
