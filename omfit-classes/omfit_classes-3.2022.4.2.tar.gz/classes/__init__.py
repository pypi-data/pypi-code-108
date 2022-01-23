import sys
import os

print('WARNING: `from omfit.classes import ...` is deprecated. Use `from omfit_classes import ...` instead!', file=sys.__stderr__)

import omfit_classes

sys.modules['classes'] = sys.modules['omfit_classes']
sys.modules['omfit.classes'] = sys.modules['omfit_classes']
