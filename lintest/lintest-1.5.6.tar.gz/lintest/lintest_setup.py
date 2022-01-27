import os

print("start execute setup.py")
os.system("python setup.py sdist --formats=gztar,zip")

print("copy ./dist/*  to ~/packages")
os.system("cp ./dist/*.* ~/packages/")
