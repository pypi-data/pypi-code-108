import core,os,sys
def main():
    try:
        lists = core.laoding()
    except FileNotFoundError:
        zhailu = open('./zhailu.file','w')
        lists = core.laoding()
    while True:
        print('[system]请选择以下操作\n[1]添加摘录\n[2]搜索摘录\n[3]退出')
        choice = input('请选择：')
        if choice == '1':
            lists = core.add(lists)
        elif choice == '2':
            keyword = input('关键词：')
            theme = input('适用主题：')
            source = input('出处：')
            author = input('作者：')
            core.Search(lists,keyword,theme,source,author)
        elif choice == '3':
            is_exit = input('是否退出[y/n] ')
            if is_exit == 'y':
                core.save(lists)
                break