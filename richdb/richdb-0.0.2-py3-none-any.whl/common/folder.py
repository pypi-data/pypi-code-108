
class Folder(list):
    def __init__(self, name):
        self.name = name

    def dir(self, nesting=0):
        offset = " "*nesting
        print('%s%s/' %(offset, self.name))

        for ele in self:
            if hasattr(ele, 'dir'):
                ele.dir(nesting+1)
            else:
                print("%s  %s" %(offset, ele))


tree = Folder('project')
tree.append('README.md')
tree.dir()
src = Folder('src')
src.append('script.py')
tree.append(src)
tree.dir()