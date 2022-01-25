import os,sys
def laoding():
    line = []
    text = ''
    zhailu = open('./zhailu.file','r')
    for i in zhailu:
        for a in i:
            if a == '\n' or a == '|' or a == '':
                line.append(text)
                text = ''
            else:
                text = text + a
        sentence = []
        theme = []
        source = []
        author = []
        time = 0
        for c in line:
                time = time + 1
                if time == 5:
                    time = 1
                elif time == 1:
                    sentence.append(c)
                elif time == 2:
                    theme.append(c)
                elif time == 3:
                    source.append(c)
                elif time == 4:
                    author.append(c)
    zhailu.close()
    print('[sysytem]文件加载成功')
    return line
def Search(the_list,keyword,theme,source,author):
    sentences = []
    themes = []
    sources = []
    authors = []
    time = 0
    for c in the_list:
        time = time + 1
        if time == 5 or time > 5:
            time = 1
        if time == 1:
            sentences.append(c)
        elif time == 2:
            themes.append(c)
        elif time == 3:
            sources.append(c)
        elif time == 4:
            authors.append(c)  
    sentences_searched = []
    if keyword != '':
        for i in sentences:
            if keyword in i:
                sentences_searched.append(i)
#   elif theme != '':
#        for i in themes:
#            if keyword in i:
#                sentences_searched.append(i)
#    elif source != '':
#        for i in sources:
#            if keyword in i:
#                sentences_searched.append(i)"
    id_ = 0
    print('已搜到与“'+keyword+'”相关摘录')
    for c in sentences_searched:
        print('['+str(id_)+']'+c)
        id_ = int(id_) + 1
    id = input('请选择：')
    id = sentences.index(sentences_searched[int(id)])
    print('[句子]'+sentences[id])
    print('[主题]'+themes[id])
    print('[出处]'+sources[id])
    print('[作者]'+authors[id])
def add(the_list):
    sentences = []
    themes = []
    sources = []
    authors = []
    time = 0
    for c in the_list:
        time = time + 1
        if time == 5:
            time = 1
        if time == 1:
            sentences.append(c)
        elif time == 2:
            themes.append(c)
        elif time == 3:
            sources.append(c)
        elif time == 4:
            authors.append(c)        
    while True:
        is_input = True
        sentence = input('[句子]')
        for i in sentences:
            if sentence == i:
                print('[错误]句子重复')
                is_input = False
        if is_input == True:
            theme = input('[主题]')
            source = input('[出处]')
            author = input('[作者]')
            the_list.append(sentence)
            if theme == '':
                the_list.append('')
            else:
                the_list.append(theme)
            if source == '': 
                the_list.append('')
            else:
                the_list.append(source)
            if author == '':
                the_list.append('')
            else:
                the_list.append(author)
            return the_list
def save(the_list):
    zhailu1 = open('zhailu1.file','w')
    sentences = []
    themes = []
    sources = []
    authors = []
    time = 0
    for i in the_list:
        time = time + 1
        if time == 5:
            time = 1
        if time == 1:
            sentences.append(i)
        elif time == 2:
            themes.append(i)
        elif time == 3:
            sources.append(i)
        elif time == 4:
            authors.append(i)
    for i in sentences:
        zhailu1.write(i)
        zhailu1.write('|'+themes[sentences.index(i)])
        zhailu1.write('|'+sources[sentences.index(i)])
        zhailu1.write('|'+authors[sentences.index(i)]+'\n')
    zhailu1.close()
    os.rename('zhailu1.file','zhailu.file')
def main():
    try:
        lists = laoding()
    except FileNotFoundError:
        zhailu = open('./zhailu.file','w')
        lists = laoding()
    while True:
        try:
            print('[system]请选择以下操作\n[1]添加摘录\n[2]搜索摘录\n[3]退出')
            choice = input('请选择：')
            if choice == '1':
                lists = add(lists)
            elif choice == '2':
                keyword = input('关键词：')
                theme = input('适用主题：')
                source = input('出处：')
                author = input('作者：')
                Search(lists,keyword,theme,source,author)
            elif choice == '3':
                is_exit = input('是否退出[y/n] ')
                if is_exit == 'y':
                    save(lists)
                    break
        except KeyboardInterrupt:
            save(lists)
            print('已退出')
            input()
            break
if __name__ == '__main__':
    main()