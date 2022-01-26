from .build import Build

# 编译代码后保存
def save(filename, target_type):
    build = Build(filename, target_type)
    code = build.code
    savefile(filename, code)

# 保存文件
def savefile(filename, code):
    if ".zpy" in filename:
        filename = filename.replace(".zpy", ".py")
    elif ".py" in filename:
        filename = filename.replace(".py", ".zpy")
    with open("./"+filename, "w") as newFile:
        newFile.write(code)