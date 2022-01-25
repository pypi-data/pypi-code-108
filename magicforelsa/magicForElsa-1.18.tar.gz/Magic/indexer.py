import json
import os
import pickle
import webbrowser
from difflib import get_close_matches
from pathlib import Path
from threading import Thread
import platform
from talk1 import talk1

if platform.system() == 'Windows':
    homedir = os.environ["USERPROFILE"]
else: homedir = os.path.expanduser('~')

indexerpth, indexerfolderpth = (os.getcwd() + "/resources/ indexer.elsa"), (os.getcwd() + "/resources/ indexerfolder.elsa")
directories = [desktop := Path(os.path.join(os.path.join(homedir), "Desktop")),
               documents := Path(os.path.join(os.path.join(homedir), "Documents")),
               downloads := Path(os.path.join(os.path.join(homedir), "Downloads")),
               music := Path(os.path.join(os.path.join(homedir), "Music")),
               videos := Path(os.path.join(os.path.join(homedir), "Videos"))]
cacheDataFile, cacheDataFolder = dict(), dict()


def read_indexer_folders(event = "") -> list:
    """To get the list of folders that should be indexed additionally"""
    try:
        with open((os.getcwd() + "/resources/ indexerpaths.elsa")) as f: return json.load(f)
    except: pass


def fsearch(mode, fname) -> None:
    """To search for file/folder in the cache"""
    cacheData = cacheDataFile if mode == "file" else cacheDataFolder
    try:
        webbrowser.open(cacheData[fname])
        print(f"{fname} found in cache")
        talk1.talk(f"opened {fname}")
    except:
        fpath = indexerpth if mode == 'file' else indexerfolderpth
        with open(fpath, "rb") as cache:
            cache_dict = pickle.load(cache)
        print("Approximate to", approx_file := get_close_matches(fname, tuple(cache_dict), n = 1, cutoff = 0.7))
        try:
            if len(approx_file) != 0 and len(approx_file[0]) != 0:
                webbrowser.open(srched_filepath := cache_dict[approx_file[0]])
                print(f"Opened {srched_filepath}")
                talk1.talk(f"Opened {approx_file}")
                cacheData[fname] = srched_filepath
            else: talk1.talk("Could not find any files", True)
        except: talk1.talk('Could not find any files', True)


def index(dataOfDirectories: dict, dataofFolders: dict, pathn) -> None:
    """[Used to index files]"""
    try:
        for name in os.listdir(pathn):
            i = Path((ine := os.path.join(pathn, name)))
            if i.is_file(): dataOfDirectories[name.split(".")[0].lower()] = ine
            elif name.startswith(".") == False and name.startswith("__") == False:
                try:
                    dataofFolders[name.lower()] = ine
                    index(dataOfDirectories, dataofFolders, i)
                except Exception as e: print(e)
    except Exception as e: print(e)


def index_files() -> None:
    """[Check if the indexer.elsa file exists.If it exists,no action is taken.If it doesnt exists,files are indexed]"""

    def _index_files():
        if not Path(indexerpth).exists():
            print("'indexer.elsa' not found", "\nIndexing files...Wait a moment...")
            try: directories.extend(read_indexer_folders())
            except: pass
            dataOfDirectories, dataOfFolders = {}, {}
            proc = [Thread(target = index, args = (dataOfDirectories, dataOfFolders, paths)) for paths in directories]
            [p.start() for p in proc]
            print("Indexing Threads:", *proc)
            [p.join() for p in proc]
            with open(indexerpth, "wb") as cache: pickle.dump(dataOfDirectories, cache)
            with open(indexerfolderpth, "wb") as cache2: pickle.dump(dataOfFolders, cache2)
            del cache, dataOfDirectories, dataOfFolders
            print("All indexing processes functions finished,files updated")
            global cacheDataFile, cacheDataFolder
            cacheDataFile, cacheDataFolder = {}, {}  # Resetting cache dict to avoid errors and such
        else: print("'indexer.elsa' found")

    Thread(target = _index_files).start()


def add_indexer_folders(event = "", path: str = "") -> None:
    """Add additional folders that should be indexed"""
    folderpth = os.getcwd() + '/resources/ indexer-paths.elsa'
    try:
        with open(folderpth) as f:
            folders = json.load(f)
            # ...Converting to set to avoid duplicates.....
            # ...Keeping it as list itself because other files expect this to be a list due to legacy reasons,etc,etc
            folders = list(set(folders.append(path)))  # ADDING PATH TO THE FOLDERS LIST
        with open(folderpth, "w") as f: json.dump(folders, f, indent = 4)
    except:
        with open(folderpth, "w") as f: json.dump([path], f, indent = 4)
    try: os.remove((os.getcwd() + "/resources/ indexer.elsa"))
    except: pass
