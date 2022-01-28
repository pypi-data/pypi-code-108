import os
import shutil

def generate_file(src_path,dict_kv,target_path):
    text=open(src_path,'r',encoding='utf-8').read()
    for k in dict_kv:
        text=text.replace("{"+k+"}",dict_kv[k])
    f_out=open(target_path,'w',encoding='utf-8')
    f_out.write(text)
    f_out.close()


def deploy(src_root="src",
           dist_root="dist",
           license_path="",
           name="quick-pypi-test",
           description="This is a quick-pypi-test Project!",
           version="",
           project_url="",
           author_name="Earthling",
           author_email="Earthling@Earth.org",
           keywords="",
           requires="",
           license="MIT",
           license_filename="LICENSE",
           github_username="",
           readme_path="",
           long_name="",
           long_description=""
           ):

    if long_description=="":
        long_description=description
    if long_name=="":
        long_name=name

    src = os.path.basename(src_root)
    if not os.path.exists(dist_root):
        os.mkdir(dist_root)
    else:
        print(f'Distribution folder already exists: {dist_root}')
        if ':' in dist_root:
            print("To prevent unexpected deleting user's userful file, when the dist_root is set like 'C:\\document\\dist', the lib will refuse to automatically delete distrition folder!")
            print("Please manually delete the folder!")
            print("Exit!")
            return
        should_delete=input(f"【Question】 Do you want to delete the folder '{dist_root}' and its all contents?(yes/no):")
        if should_delete.lower()=="yes":
            shutil.rmtree(dist_root)
            os.mkdir(dist_root)
        else:
            print("You choose NO. Please manually delete the distribution folder that already exists!")
            print("Exit!")
            return

    current_path = os.path.dirname(os.path.realpath(__file__))
    license_path_mit=f'{current_path}/template/LICENSE'
    manifest_path=f'{current_path}/template/MANIFEST.in'
    if readme_path=="":
        readme_path=f'{current_path}/template/README.md'
    else:
        if not os.path.exists(readme_path):
            print("README.md does not exist!")
            return
    setup_cfg_path=f'{current_path}/template/setup.cfg'
    setup_path=f'{current_path}/template/setup.py'

    if license_path!="":
        if os.path.exists(license_path):
            # filename, file_extension = os.path.splitext(license_path)
            shutil.copyfile(license_path, f'{dist_root}/{license_filename}')
    else:
        shutil.copyfile(license_path_mit, f'{dist_root}/{license_filename}')

    manifest_model={
        "src":src,
        "license_filename":license_filename
    }

    generate_file(manifest_path,manifest_model,f'{dist_root}/MANIFEST.in')

    readme_model={
        "name":name,
        "long_name":long_name,
        "long_description":long_description,
        "license":license,
        "version":version
    }

    generate_file(readme_path, readme_model, f'{dist_root}/README.md')
    #
    requires_list_str=""

    if requires.strip()=="":
        requires_list_str=""
    else:
        requires_list = [f'"{r}"' for r in requires.split(";")]
        requires_list_str=','.join(requires_list)

    setup_model={
        "name":name,
        "description":description,
        "version":version,
        "project_url":project_url,
        "author_name":author_name,
        "author_email":author_email,
        "keywords":keywords,
        "src":src,
        "requires":requires_list_str,
        "license":license,
        "license_filename":license_filename,
        "github_username":github_username
    }

    if github_username=="" or project_url=="":
        setup_path = f'{current_path}/template/setup_no_urls.py'
        generate_file(setup_path, setup_model, f'{dist_root}/setup.py')
    else:
        generate_file(setup_path, setup_model, f'{dist_root}/setup.py')

    setup_cfg_model={
        "license_filename":license_filename
    }

    generate_file(setup_cfg_path, setup_cfg_model, f'{dist_root}/setup.cfg')

    # copy src folder
    if os.path.exists(src_root):
        print("copying src_root...")
        shutil.copytree(src_root, f'{dist_root}/{src}')

def get_next_version(version,max_number_micro=5,max_number_minor=5):
    parts=version.split(".")
    major=int(parts[0])
    minor=int(parts[1])
    micro=int(parts[2])
    if micro>=max_number_micro:
        minor+=1
        micro=0
        if minor>max_number_minor:
            major+=1
            minor=0
        return f'{major}.{minor}.{micro}'
    else:
        micro+=1
        return f'{major}.{minor}.{micro}'


def auto_deploy(name="quick-pypi-test",dists_root="dists", version="auto",cwd="", max_number_micro=20,max_number_minor=20, pypi_token="", test=False, **kwargs):
    if cwd!="":
        dists_root=os.path.join(cwd,dists_root)
    if not os.path.exists(dists_root):
        os.mkdir(dists_root)
    if version=="auto":
        version_path=f'{dists_root}/VERSION'
        current_version="0.0.0"
        if os.path.exists(version_path):
            vv=open(version_path,'r',encoding='utf-8').read().strip()
            if vv=="":
                current_version="0.0.0"
            else:
                current_version=vv
        next_version=get_next_version(current_version,max_number_micro=max_number_micro,max_number_minor=max_number_minor)
        version=next_version
    dist_root=f'{dists_root}/{version}'
    if os.path.exists(dist_root):
        print("WARNING: Version Exists! ",dist_root)
    deploy(name=name, version=version, dist_root=dist_root, **kwargs)
    if version=="auto":
        f_out=open(f"{dists_root}/VERSION","w",encoding='utf-8')
        f_out.write(version)
        f_out.close()
    print("====================Building and Uploading================")
    if test:
        upload_test_package(dist_root,token_path_or_str=pypi_token,cwd=cwd)
    else:
        upload_package(dist_root, token_path_or_str=pypi_token, cwd=cwd)

def upload_package(dist_root,token_path_or_str,cwd=""):
    os.chdir(dist_root)
    print("Working directory: ", dist_root)
    # delete dist files
    if os.path.exists("dist"):
        for file in os.listdir("dist"):
            if file.endswith(".whl") or file.endswith(".gz"):
                print("delete: ", "dist/" + file)
                os.remove("dist/" + file)
    # build c extensions
    if os.path.exists("src_cython"):
        os.chdir("src_cython")
        os.system("python build_cython_libs.py")

    os.chdir(dist_root)

    print("Starting to build...")
    os.system("python -m build")
    print()
    print("Starting to check...")
    os.system("twine check dist/*")
    print()
    print("Starting to upload...")
    username = "__token__"
    # token_path = "../pypi_upload_token.txt"
    if cwd!="":
        os.chdir(cwd)
    if token_path_or_str!="":
        if os.path.exists(token_path_or_str):
            token_str = open(token_path_or_str, 'r', encoding='utf-8').read().strip()
        else:
            token_str = token_path_or_str
        os.system(f"twine upload {dist_root}/dist/* -u {username} -p {token_str}")

def upload_test_package(dist_root,token_path_or_str,cwd=""):
    os.chdir(dist_root)
    print("Working directory: ", dist_root)
    # delete dist files
    if os.path.exists("dist"):
        for file in os.listdir("dist"):
            if file.endswith(".whl") or file.endswith(".gz"):
                print("delete: ", f"{dist_root}/dist/" + file)
                os.remove(f"{dist_root}/dist/" + file)
    # build c extensions
    if os.path.exists(f"src_cython"):
        os.chdir("src_cython")
        os.system("python build_cython_libs.py")

    os.chdir(dist_root)

    print("Starting to build...")
    os.system("python -m build")
    print()
    print("Starting to check...")
    os.system("twine check dist/*")
    print()
    print("Starting to upload...")
    username = "__token__"
    # token_path = "../pypi_test_upload_token.txt"
    if cwd!="":
        os.chdir(cwd)

    if token_path_or_str!="":
        if os.path.exists(token_path_or_str):
            token_str = open(token_path_or_str, 'r', encoding='utf-8').read().strip()
        else:
            token_str=token_path_or_str
        os.system(f"twine upload --repository testpypi {dist_root}/dist/* -u {username} -p {token_str}")


if __name__=="__main__":
    version="0.0.1"
    for i in range(1,50):
        print(version)
        version=get_next_version(version)

