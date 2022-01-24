import socket
# from pathlib import Path
from transparentpath import Path
import os
import dotenv

dotenv.load_dotenv()


def get_root_path() -> str:
    # Renvoie suivant la config le chemin parent de research_and_development
    host = socket.gethostname()
    force_local = os.getenv("force_local", "False").lower() == "true"
    under_ubuntu = (os.environ['GDMSESSION'] == 'ubuntu')
    if not force_local:
        nas_connected = Path(r"/media/SERVEUR/production/research_and_development/",
                             fs="local").is_dir() if under_ubuntu else \
            Path(r"/davs://advestis.synology.me:5006/", fs="local").isdir()
    else:
        nas_connected = False

    if host in ["ADLAPTOPCG", "LAPTOP-CG"]:
        # laptop Ubuntu session
        # local = not Path("Y:/").is_dir()
        if not nas_connected:
            rootpath = (Path(r"/home/cgeissler/local_data", fs="local") if under_ubuntu
                        else Path(r"C:/Users/Christophe Geissler/", fs="local"))
        else:
            rootpath = Path(r"/media/SERVEUR/production/", fs="local") if under_ubuntu else \
                       Path(r"/davs://advestis.synology.me:5006/", fs="local")
    elif host == "cgeissler-portable":
        # Session laptop sous WIndows
        # local = False
        rootpath = Path(r"/davs://advestis.synology.me:5006/", fs="local") if nas_connected \
            else Path(r"C:/Users/Christophe Geissler/", fs="local")
        # rootpath = rootpath / r"research_and_development/Reduction_de_Dimension_(NMTF)/Article_PF_clustering/"
    else:
        # session machine fixe Ubuntu
        # local = False
        rootpath = Path(r"/media/SERVEUR/production/", fs="local") \
            if nas_connected else Path(r"/home/cgeissler/local_data/", fs="local")
    return rootpath


