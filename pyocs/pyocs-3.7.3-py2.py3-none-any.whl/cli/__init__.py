from .Pyocs_cli import cli
import requests, os


user = os.environ['USER'] # pyocs命令行使用场景较多，使用linux中USER环境变量传递当前用户，虽然并非100%准确，但是具备统计意义