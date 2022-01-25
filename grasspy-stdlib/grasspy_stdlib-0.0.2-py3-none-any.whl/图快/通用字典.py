_锚点字典 = {
    '上':   'n',
    '下':   's',
    '右':   'e',
    '左':   'w',
    '左上': 'nw',
    '左下': 'sw',
    '右上': 'ne',
    '右下': 'se',
    '左右': 'ew',
    '上下左右': 'nsew',
    '居中': 'center',
}

_颜色字典 = {
    '红色': 'red',
    '黄色': 'yellow',
    '蓝色': 'blue',
    '黑色': 'black',
    '白色': 'white',
    '灰色': 'grey',
    '绿色': 'green',
    '紫色': 'purple',
    '橙色': 'orange',
    '洋红': 'magenta',
    '海贝色': 'seashell',
    '粉红': 'pink',
    '棕色': 'brown',
    '金色': 'gold',
    '银色': 'silver',
    '青色': 'cyan',
    '番茄色': 'tomato',
}

_对齐字典 = {
    '居中': 'center',
    '左边': 'left',
    '右边': 'right',
}

_边框样式字典 = {
    '凹陷': 'sunken',
    '凸起': 'raised',
    '压线': 'groove',
    '脊线': 'ridge',
    '扁平': 'flat'
}

_部件通用选项值字典 = {}
_部件通用选项值字典.更新(_颜色字典)
_部件通用选项值字典.更新(_对齐字典)
_部件通用选项值字典.更新(_边框样式字典)
_部件通用选项值字典.更新(_锚点字典)

_验证字典 = {
    '焦点':     'focus',
    '得焦点':   'focusin',
    '失焦点':   'focusout',
    '按键':     'key',
    '全部':     'all',
    '无':       'none'
}

_部件通用选项字典 = {
    '活动背景色':   'activebackground', 
    '活动前景色':   'activeforeground', 
    '锚点':         'anchor',
    '背景色':       'background', 
    '位图':         'bitmap', 
    '边框宽度':     'borderwidth', 
    '鼠标样式':     'cursor',
    '禁用时前景色':  'disabledforeground', 
    '字体':         'font', 
    '前景色':       'foreground',
    '高亮背景':     'highlightbackground', 
    '高亮颜色':     'highlightcolor',
    '高亮厚度':     'highlightthickness', 
    '图像':         'image', 
    '对齐':         'justify',
    '水平边距':     'padx', 
    '垂直边距':     'pady', 
    '边框样式':     'relief', 
    '获得焦点':     'takefocus', 
    '文本':         'text',
    '文本变量':     'textvariable', 
    '下划线':       'underline', 
    '分行长度':     'wraplength'
}

_菜单配置选项字典 = {
    '标签': 'label',
    '菜单': 'menu',
    '命令': 'command',
    '下划线': 'underline',
}
