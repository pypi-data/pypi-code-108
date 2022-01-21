from main_paras import info

def addTest(user):
    pf = info.getProfile('feng.gao@laipac.com')
    pf['user']= user
    info.setProfile(pf)
    info.show()
    

if __name__ == "__main__":

##    addTest('hh_1')
##    addTest('hh_2')
##    addTest('hh_3')
##    addTest('hh_4')
##    addTest('hh_5')
##    addTest('hh_6')
##    addTest('hh_7')
##    addTest('hh_8')
##    addTest('hh_9')
##
##    info.clear()
    info.show()

 
##    pf=info.getProfile('feng.gao@laipac.com')
##
##    print('got', pf)
##
##    pf['user']='feng.gao@laipac.com'
##
##    print('modified', pf)
##              
##    print('get again', info.getProfile('aa'))
