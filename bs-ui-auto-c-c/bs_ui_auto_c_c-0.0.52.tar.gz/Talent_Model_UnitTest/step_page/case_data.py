
class case_data:
    """
    用于存储测试用例数据
    """

    def __init__(self):
        pass

    class cases_data_dict:
        """
        所有测试用例所以来的基础数据
        """
        login_info = {'username': 'root600684@beisen.com', 'password': 'aa123456'}

        def __init__(self):
            pass
        add_talent_model_date = {'预期结果': '添加成功'}
        delete_talent_model_date = {'预期结果': '删除成功'}

        upload_file = {
            'file_path':'/step_page/upload.txt'
        }

    class get_tools_data:
        """
        查询工具所有依赖数据
        """

        def __init__(self):
            pass


