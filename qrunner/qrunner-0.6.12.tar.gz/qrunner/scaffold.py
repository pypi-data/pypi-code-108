import os.path
import sys

run_content = """
import qrunner


if __name__ == '__main__':
    qrunner.main(
        platform='android',
        serial_no='UJK0220521066836',
        pkg_name='com.qizhidao.clientapp'
    )

'''
:param platform: 平台，如browser、android、ios
:param serial_no: 设备id，如UJK0220521066836、00008020-00086434116A002E
:param pkg_name: 应用包名，如com.qizhidao.clientapp、com.qizhidao.company
:param browser_name: 浏览器类型，如chrome、其他暂不支持
:param case_path: 用例路径
:param rerun: 失败重试次数
:param concurrent: 是否需要并发执行，只支持platform为browser的情况
'''
"""
case_android_content = """
import qrunner


class TestMy(qrunner.TestCase):
    def test_go_my(self):
        self.element(resourceId='id/bottom_btn').click()
        self.element(resourceId='id/bottom_view', index=3).click()
        assert self.element(text='我的订单').exists(timeout=3)
        self.driver.screenshot('test.png')
"""

require_content = """qrunner
"""

ignore_content = "\n".join(
    ["allure-results/*", "__pycache__/*", "*.pyc", "report.html", ".idea/*"]
)


def init_scaffold_project(subparsers):
    parser = subparsers.add_parser(
        "create", help="Create a new project with template structure."
    )
    parser.add_argument(
        "project_name", type=str, nargs="?", help="Specify new project name."
    )
    return parser


def create_scaffold(project_name):
    """ create scaffold with specified project name.
    """

    def create_folder(path):
        os.makedirs(path)
        msg = f"created folder: {path}"
        print(msg)

    def create_file(path, file_content=""):
        with open(path, "w", encoding="utf-8") as f:
            f.write(file_content)
        msg = f"created file: {path}"
        print(msg)

    create_folder(project_name)
    create_file(
        os.path.join(project_name, "run.py"),
        run_content,
    )
    create_file(
        os.path.join(project_name, "../.gitignore"),
        ignore_content,
    )
    create_file(
        os.path.join(project_name, "requirements.txt"),
        require_content,
    )
    create_file(
        os.path.join(project_name, "test_demo.py"),
        case_android_content,
    )
    # show_tree(project_name)
    return 0


def main_scaffold_project(args):
    sys.exit(create_scaffold(args.project_name))

