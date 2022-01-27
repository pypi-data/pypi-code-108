import time
import os
from os.path import exists
import sys
import argparse
from pywinauto.application import Application
import keyboard
import yaml

__version__ = "1.1.5"
def main():
    if not(exists("config/config.yaml")):
        print("Emplena el fitxer de configuracio de Base de Dades a config/config.yaml")
        article_info = [
            {
            'fitxer.pbix' : '../../powerBI/apis.pbix',
            }
        ]
        with open("config/config.yaml", 'w') as yamlfile:
            data = yaml.dump(article_info, yamlfile)

    with open("config/config.yaml", "r") as yamlfile:
        data = yaml.load(yamlfile, Loader=yaml.FullLoader)
    
    parser = argparse.ArgumentParser(description='Serveix per actualitzar dashboard de PowerBI desktop localment.')
    parser.add_argument("--init-wait", help = "temps d'espera d'obertura del PowerBI. Per defecte es 60 segons.", default = 60, type = int, metavar="NUM_SEC")
    parser.add_argument("--refresh-wait", help = "Temps d'espera despres de actualitzar. Per defecte es 60 segons.", default = 60, type = int, metavar="NUM_SEC")
    parser.add_argument('-f', '--file', help='Especificar la ruta del fitxer a actualitzar. Per defecte es: '+ data[0]['fitxer.pbix'], default=data[0]['fitxer.pbix'], metavar="RUTA")
    parser.add_argument('-q', '--quiet', help='Nomes mostra els errors i el missatge de acabada per pantalla.', action="store_false")
    parser.add_argument('-v', '--versio', help='Mostra la versio', action='version', version='refresh-PowerBI v'+__version__)
    args = parser.parse_args()



    workbook = args.file
    PROCNAME = "PBIDesktop.exe"

    if args.quiet:
        print("Obrint el document")
    os.system('start "" "' + workbook + '"')
    if args.quiet:
        print("Esperant ",args.init_wait," segons")
    time.sleep(args.init_wait)

    if args.quiet:
        print("Identificant finestra de PowerBI")
    app = Application(backend = 'uia').connect(path = PROCNAME)
    win = app.window(title_re = '.*Power BI Desktop')
    win.set_focus()
    win.Home.click_input()

    if args.quiet:
        print("Actualitzant")
    win.Refresh.click_input()
    time.sleep(args.refresh_wait)

    if args.quiet:
        print("guardant")
    keyboard.send("ctrl+s")

    print("Done")

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)
        sys.exit(1)