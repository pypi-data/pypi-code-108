from kwtools.tools1.utils_requests import myRequest

req = myRequest().req


def get_wyy_mp3(save_file_name="", save_folder_path=".", wyy_url="https://music.163.com/song?id=505688656&userid=80581305"):
    id = re.findall(r"id=(\d+)", wyy_url)
    id = id[0] if id else ""
    if id == "":
        k_success = "False"
        k_msg = "找不到id\n"
    else:
        api_url = "https://tenapi.cn/wyy?id=" + id
        print(f"api_url: {api_url}")
        res_obj = req(api_url, is_obj=True)
        res_dict = res_obj.json()
        print(res_dict)
        if res_dict.get("msg") == "解析成功":
            mp3_url = res_dict.get("url", "")
            res_obj = req(mp3_url, is_obj=True, use_session=True)
            res_content = res_obj.content
            mp3_content = res_content
            # 存储mp3音频
            if save_file_name == "":
                save_file_name = f"网易云音乐_{get_sim_today_date()}_{get_sim_this_time()}"
            save_full_path = f"{save_folder_path}/{save_file_name}.mp3"
            with open(save_full_path, "wb") as f:
                f.write(mp3_content)
            k_success = "True"
            k_msg = f"v1: 音乐'{save_file_name}':下载成功"
        else:
            k_success = "False"
            k_msg = "v1: api接口解析id失败"

    response_dict = {
        "k_success" : k_success, "k_msg" : k_msg
    }
    return response_dict


def get_wyy_mp3_v2(save_file_name="", save_folder_path=".", wyy_url="https://music.163.com/song?id=505688656&userid=80581305"):
    """
        这个api的解析能力比上面的强, 基本上上面解析不出来的, 这个都行, 可屌了"
        有时候在python运行这个api也会经常连接失败, 但是到浏览器上解析又是有用的, 很奇怪...
        比如这个:
            https://www.apicp.cn/API/wyy/api.php?id=509252160
            https://www.apicp.cn/API/wyy/api.php?id=436514221
    """

    id = re.findall(r"id=(\d+)", wyy_url)
    id = id[0] if id else ""
    if id == "":
        k_success = "False"
        k_msg = "找不到id\n"
    else:
        api_url = "https://www.apicp.cn/API/wyy/api.php?id=" + id
        print(f"api_url: {api_url}")
        res_obj = req(api_url, is_obj=True, use_session=True)
        res_content = res_obj.content
        if res_content:
            print("v2: 解析成功")
            mp3_content = res_content
            # 存储mp3音频
            if save_file_name == "":
                save_file_name = f"网易云音乐_{get_sim_today_date()}_{get_sim_this_time()}"
            save_full_path = f"{save_folder_path}/{save_file_name}.mp3"
            with open(save_full_path, "wb") as f:
                f.write(mp3_content)
        else:
            print("v2: 解析失败")


def get_mp3(save_file_name="", wyy_url="https://music.163.com/song?id=505688656&userid=80581305"):
    """
        save_file_name: 不能包含"/"等特殊字符!!  (用逗号取代"/")
    """
    save_folder_path = FILE_PATH_FOR_DESKTOP
    dic = get_wyy_mp3(save_file_name=save_file_name, save_folder_path=save_folder_path, wyy_url=wyy_url)
    if dic.get("k_success") == "False":
        get_wyy_mp3_v2(save_file_name=save_file_name, save_folder_path=save_folder_path, wyy_url=wyy_url)


def main():
    get_mp3()


if __name__ == '__main__':
    print("start test!")
    main()
    print("\n\n\neverything is ok!")
