import subprocess
def run_command(s,error_file):
    print('run command:',s)
    t = subprocess.call(s,shell=True) 
    if t != 0:
        error_file.write(s)
        error_file.write('\n')
    return t
def main():
    error_file = open('error_log.std','w')
    error_file.write('wrong command:\n')
    apt_commands=[
        'sudo apt-get install git -y',
        'sudo apt-get install gcc g++ gfortran -y',
        'sudo apt-get install texlive texlive-science -y',
        'python -m pip install yxspkg_pip --user',
    ]
    for i in apt_commands:
        t = run_command(i,error_file)
        
    python_module = ['lxml','matplotlib','pandas','numpy','scipy','imageio',
                     'git+https://gitee.com/blacksong/SciencePlots.git',
                     'rsa','tushare','PyQt5','lxml','you-get','quandl',
                     'mpl_finance','pandas_datareaderf','twine','cheroot','opencv-python',
                     'xlrd','pyqtgraph','web.py','imageio-ffmpeg','meshio']
    for i in python_module:
        command = 'python -m yxspkg_pip install '+i +' --user'
        run_command(command,error_file)
if __name__=='__main__':
    main()
