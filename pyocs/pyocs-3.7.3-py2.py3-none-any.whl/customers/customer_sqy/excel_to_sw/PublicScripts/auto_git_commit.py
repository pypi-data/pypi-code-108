import os

#--------------------------------------------------------
#  创建提交代码的log
#--------------------------------------------------------
def creategitlog(modeid):

    gitlog = ("[config][chaoye]["+modeid+"]config HD\r\r"
         +"[what]大货软件\r"
         +"[why]客户需求\r"
         +"[how]脚本自动生成生成软件\r\n")
    return gitlog

def execPush(branch):
    print(str(branch))
    branch = branch.strip()
    os.system('git gt-dpush origin '+branch)    

def autogitcommit(modeid):
    # 自动填写log信息
    log = creategitlog(modeid)

    os.system('git add .')
    os.system('git commit -m '+log)

    # 自动提交代码

    getGitSHA = execCmd('git rev-parse --short HEAD')
    getGitBranch = execCmd('git symbolic-ref --short -q HEAD')
    os.system('git reset HEAD^^ --hard')
    os.system('git pull')
    os.system('git cherry-pick '+getGitSHA)
    execPush(getGitBranch)
    
    print("####################")
    print("自动提交代码成功")
    print("####################")

def execCmd(cmd):  
    r = os.popen(cmd)  
    text = r.read()  
    r.close()  
    return text
