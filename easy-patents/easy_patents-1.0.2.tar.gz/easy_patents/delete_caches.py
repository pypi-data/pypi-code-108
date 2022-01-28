import configparser
from datetime import datetime, timedelta
import os
import glob


def delete_caches(delete_before=45):
    now = datetime.now()
    expire_date = now - timedelta(days=int(delete_before))
    dir_name = os.path.dirname(__file__)
    conf_file = os.path.join(dir_name, 'config/config.ini')

    config = configparser.ConfigParser()
    config.read(conf_file)
    data_dir = config['DirPath']['data_dir']
    search_path = os.path.join(data_dir, "**", "*")
    for file_path in glob.glob(search_path, recursive=True):
        ctime = datetime.fromtimestamp(os.path.getctime(file_path))
        if os.path.isfile(file_path) and expire_date > ctime:
            print("deleting %s" % file_path)
            os.remove(file_path)


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("usage: %s <integer>" % sys.argv[0]) 
        print("for example:") 
        print("if you want to delete 30 days and older caches,") 
        print("you can write:") 
        print("%s 30" % sys.argv[0]) 
        exit()
    delete_before = sys.argv[1]
    delete_caches(delete_before)
