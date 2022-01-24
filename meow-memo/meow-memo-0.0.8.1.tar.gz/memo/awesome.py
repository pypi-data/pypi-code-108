# https://github.com/vinta/awesome-python/raw/master/README.md
# https://github.com/vinta/awesome-python/raw/master/LICENSE
import requests
import re
from .files import update_data


def run(argdict):
    v=argdict.get("verbose") or argdict.get("v")
    sess = requests.session()
    lic = sess.get(
        r"https://github.com/vinta/awesome-python/raw/master/LICENSE")
    print("awesome-python LICENSE:")
    print("\n".join("    "+i for i in lic.text.split("\n")))
    content = sess.get(
        r"https://github.com/vinta/awesome-python/raw/master/README.md")
    t = content.text
    pattern = r"\* \[([\s\S]+?)\]\((http.+?)\)([\s\S]*?)[\r\n]"
    fa = re.findall(pattern, t)
    # print(fa[0])
    for name, url, desc in fa:
        if(desc.startswith(" - ")):
            content = "\n".join([desc[3:], url])
        else:
            content = "%s: %s"%(name, url)
        update_data(name, content)
        if(v):
            print('"',name,'"',end=" ",sep="")


if(__name__ == '__main__'):
    run()
