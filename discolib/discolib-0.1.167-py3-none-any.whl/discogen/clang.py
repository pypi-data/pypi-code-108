from discolib.discogen.bases import LangGenerator
from discolib.discogen.config import Config
from discolib.discogen import discogen


import os
from distutils import dir_util
from pathlib import Path
import struct

class ClangGenerator(LangGenerator):

    SEARCH_KEY = "#pragma region DiscoGen"
    END_KEY = "#pragma endregion DiscoGen"
    TYPE_MAP = {
        'B': 'byte_attr',
        'I': 'uint_attr',
        'f': 'float_attr'
    }
    ATTR_PREFIX = 'disco_attr_'
    FIRST_ATTR_PORT = 0x43

    def __init__(self, cfg: Config):
        super().__init__(cfg)
        self.src_path = discogen.CODEGEN_PATH / 'clang'
        self.dest_path = Path(os.getcwd()) / 'disco'
        print(f'Generating C code at {os.getcwd()}...')
        dir_util.copy_tree(self.src_path, os.getcwd())

    def _generate_attribute_header(self):
        attr_decl = ''
        for attr in self.attributes:
            attr_decl += f'extern {self.TYPE_MAP[attr.type]} {self.ATTR_PREFIX}{attr.name};\n'
        content = f"""

#define N_ATTR {len(self.attributes)}

/**
 *  @brief User-defined attributes.
 */
{attr_decl}
"""
        return content

    def _generate_attribute_source(self):
        attr_def = ''
        for attr in self.attributes:
            attr_def += f'{self.TYPE_MAP[attr.type]} {self.ATTR_PREFIX}{attr.name} = {{.setpoint_default = {attr.default}}};\n'
        
        port = self.FIRST_ATTR_PORT
        attr_array = []
        for attr in self.attributes:
            attr_string = (f'{{.port = {hex(port)},' +
                f'.size = {struct.calcsize(attr.type)},' +
                f'.readback = (uint8_t*)&{self.ATTR_PREFIX}{attr.name}.readback,' +
                f'.setpoint = (uint8_t*)&{self.ATTR_PREFIX}{attr.name}.setpoint,' +
                f'.setpoint_default = (uint8_t*)&{self.ATTR_PREFIX}{attr.name}.setpoint_default,' +
                f'.name = "{attr.name}",' +
                f'.type = \'{attr.type}\'}}')
            attr_array.append(attr_string)
            port += 1
        content = f"""

/* User attribute definitions */
{attr_def}

/* All DISCo attributes */
disco_attr disco_attrs[N_ATTR] = {{{','.join(attr_array)}}};
"""
        return content

    def _substitute_file(self, file_path, subst_func):
        with open(file_path) as subst_file:
            buf = subst_file.readlines()
        
        with open(file_path, 'w') as subst_file:
            write_line = True
            for line in buf:
                if self.SEARCH_KEY == line.strip():
                    write_line = False
                    cont = subst_func()
                    line = line + cont
                    subst_file.write(line)
                if self.END_KEY == line.strip():
                    write_line = True
                if write_line:
                    subst_file.write(line)
            subst_file.write('\n') # Trailing newline
    
    def write_attributes(self):
        attr_h = self.dest_path / 'attr.h'
        attr_c = self.dest_path / 'attr.c'
        self._substitute_file(attr_h, self._generate_attribute_header)
        self._substitute_file(attr_c, self._generate_attribute_source)
