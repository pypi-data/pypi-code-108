import os


include_list = ";.json;.cu;.cpp;.cuh;.h;.hpp;.cpp;makefile;cmakelists.txt;.sh;.bash;.py;.c;"

def filter_content(content, variable_template):
    found_variable = False
    for k, v in variable_template:
        key = "${@" + k + "}"
        if not found_variable:
            if content.find(key) == -1:
                continue
            
            found_variable = True

        content = content.replace(key, v)
    return content, found_variable


def inv_filter_content(content, variable_template):
    found_variable = False
    for k, v in variable_template:
        key = "${@" + k + "}"
        if not found_variable:
            if content.find(v) == -1:
                continue
            
            found_variable = True

        content = content.replace(v, key)
    return content, found_variable


def process_code_template(proj_dir, namelist, variable_template, filter_func=filter_content):

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
            
            content = open(full_path, "r").read()
            new_content, found_variable = filter_func(content, variable_template)
            if found_variable:
                print(f"Process variables {full_path}")
                open(full_path, "w").write(new_content)
