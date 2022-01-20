from invoke import Collection, Program
import sykel
namespace = Collection()
namespace.add_collection(Collection.from_module(sykel.version))
namespace.add_collection(Collection.from_module(sykel.package))
program = Program(namespace=namespace, version=sykel.__version__)
