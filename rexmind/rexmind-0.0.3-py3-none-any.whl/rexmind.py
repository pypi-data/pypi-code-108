from itertools import product
from PIL import Image
import os
import zipfile
import shutil


class rexmind(object):
    def __init__(self):
        super()

    def xmind2png(self, path, path1):
        if '.' not in path:
            path = path + '.xmind'
        if '.' not in path1:
            path1 = path1 + '.png'
        i = path.find('.')
        n = path[:i]+'.zip'
        os.rename(path, n)
        file = zipfile.ZipFile(n)
        file.extractall(path[:i])
        file.close()
        shutil.move(path[:i]+'/Thumbnails/thumbnail.png', path1)
        os.rename(n, path)
        shutil.rmtree(path[:i])

    def convertPixel(self, r, g, b, a=1):
        color = "#%02X%02X%02X" % (r, g, b)
        opacity = a
        return (color, opacity)

    def xmind2svg(self, path, path1):
        self.xmind2png(path, path)
        if '.' not in path:
            path = path + '.png'
        if '.' not in path1:
            path1 = path1 + '.svg'
        r = path
        root, ext = os.path.splitext(r)

        image = Image.open(r)
        mode = image.mode
        pixels = image.load()
        width, height = image.size

        if "RGB" in mode:
            output = '<svg width=" % d" height=" % d" viewBox="0 0 % d % d" xmlns="http: // www.w3.org/2000/svg">' % (
                width, height, width, height)

            for r in range(height):
                for c in range(width):
                    color, opacity = self.convertPixel(*pixels[c, r])
                    output += '<rect x=" %d" y=" %d" width="1" height="1" fill=" % s" fill-opacity=" % s"/>' % (
                        c, r, color, opacity)

            output += "</svg>"

            with open(root + ".svg", "w") as f:
                f.write(output)

    def sypng2svg(self, path, path1):
        if '.' not in path:
            path = path + '.png'
        if '.' not in path1:
            path1 = path1 + '.svg'
        self.sypng2png(path, path)
        r = path
        root, ext = os.path.splitext(r)

        image = Image.open(r)
        mode = image.mode
        pixels = image.load()
        width, height = image.size

        if "RGB" in mode:
            output = '<svg width=" % d" height=" % d" viewBox="0 0 % d % d" xmlns="http: // www.w3.org/2000/svg">' % (
                width, height, width, height)

            for r in range(height):
                for c in range(width):
                    color, opacity = self.convertPixel(*pixels[c, r])
                    output += '<rect x=" %d" y=" %d" width="1" height="1" fill=" % s" fill-opacity=" % s"/>' % (
                        c, r, color, opacity)

            output += "</svg>"

            with open(root + ".svg", "w") as f:
                f.write(output)

    def sypng2png(self, path, path1):
        if '.' not in path:
            path = path + '.png'
        if '.' not in path1:
            path1 = path1 + '.png'
        img = Image.open(path)
        width, height = img.size
        for pos in product(range(width), range(height)):
            if sum(img.getpixel(pos)[:3]) == 0 or sum(img.getpixel(pos)[:3]) >= 400:
                img.putpixel(pos, (255, 255, 255))
        img.save(path1)

    def sypng2md(self, path, path1):
        self.sypng2png(path, path)
        if '.' not in path:
            path = path + '.png'
        if '.' not in path1:
            path1 = path1 + '.md'
        with open(path1, 'w')as md:
            md.write('![]({})'.format(path))

    def xmind2md(self, path, path1):
        self.xmind2png(path, path)
        if '.' not in path:
            path = path + '.png'
        if '.' not in path1:
            path1 = path1 + '.md'
        with open(path1, 'w')as md:
            md.write('![]({})'.format(path))
