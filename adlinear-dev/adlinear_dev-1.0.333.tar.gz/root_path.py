import socket
from pathlib import Path
import os
import dotenv

dotenv.load_dotenv()


def get_root_path():
    # Renvoie suivant la config le chemin parent de research_and_development
    host = socket.gethostname()
    force_local = os.getenv("force_local", "False").lower() == "true"
    under_ubuntu = (os.environ['GDMSESSION'] == 'ubuntu')
    if not force_local:
        nas_connected = Path(r"/media/SERVEUR/production/research_and_development/").is_dir() if under_ubuntu else \
            Path(r"/davs://advestis.synology.me:5006/").isdir()
    else:
        nas_connected = False

    if host in ["ADLAPTOPCG", "LAPTOP-CG"]:
        # laptop Ubuntu session
        # local = not Path("Y:/").is_dir()
        if not nas_connected:
            rootpath = (Path(r"/home/cgeissler/local_data") if under_ubuntu
                        else Path(r"C:/Users/Christophe Geissler/"))
        else:
            rootpath = Path(r"/media/SERVEUR/production/") if under_ubuntu else \
                       Path(r"/davs://advestis.synology.me:5006/")
    elif host == "cgeissler-portable":
        # Session laptop sous WIndows
        # local = False
        rootpath = Path(r"/davs://advestis.synology.me:5006/") if nas_connected \
            else Path(r"C:/Users/Christophe Geissler/")
        # rootpath = rootpath / r"research_and_development/Reduction_de_Dimension_(NMTF)/Article_PF_clustering/"
    else:
        # session machine fixe Ubuntu
        # local = False
        rootpath = Path(r"/media/SERVEUR/production/") if nas_connected else Path(r"/home/cgeissler/local_data/")
    return rootpath


