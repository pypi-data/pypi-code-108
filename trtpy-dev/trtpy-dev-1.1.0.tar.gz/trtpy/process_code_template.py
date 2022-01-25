import os


include_list = ";.json;.cu;.cpp;.cuh;.h;.hpp;.cpp;makefile;cmakelists.txt;.sh;.bash;.py;.c;"

def filter_content(content, variable_template):
    for k, v in variable_template:
        content = content.replace("${@" + k + "}", v)
    return content


def process_code_template(proj_dir, namelist, variable_template):

    for file in namelist:
        if proj_dir is None:
            full_path = file
        else:
            full_path = os.path.join(proj_dir, file)

        if os.path.isfile(full_path):
            basename = os.path.basename(full_path).lower()
            suffix = os.path.splitext(basename)[1]
            if not (include_list.find(";" + basename + ";") != -1 or suffix != "" and include_list.find(suffix) != -1):
                continue
            
            print(f"Process variables {full_path}")
            content = open(full_path, "r").read()
            open(full_path, "w").write(filter_content(content, variable_template))
