import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['OMP_NUM_THREADS'] = '1'

# os.environ['RWROOT']=os.path.join(os.path.dirname(__file__), "../../../../../")

__path__ = __import__('pkgutil').extend_path(__path__, __name__)
