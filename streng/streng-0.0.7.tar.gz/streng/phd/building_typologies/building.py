from dataclasses import dataclass, field

@dataclass
class RCTypology:
    name: str = None
    code: str = field(init=False)
    storeys: int = field(init=False)
    height_level: str = field(init=False)
    structural_system: str = field(init=False)
    infill_pattern: str = field(init=False)
    code_level: str = field(init=False)

    @classmethod
    def from_old_analyses_name(cls, old_name):
        spl = old_name.split('_')

        cls.storeys = int(spl[0])

        if spl[1] == 'du':
            cls.structural_system = 'dual'
        elif spl[1] == 'fr':
            cls.structural_system = 'frame'
        else:
            cls.structural_system = 'oops!'

        if spl[2] == '59':
            cls.code = 'bd59'
        elif spl[2] == '84':
            cls.code = 'pa84'
        elif spl[2] == 'eak':
            cls.code = 'eak'
        else:
            cls.code = 'oops'

        if spl[3] == 'bare':
            cls.infill_pattern = 'bare'
        elif spl[3] == 'inf':
            cls.infill_pattern = 'infilled'
        elif spl[3] == 'pil':
            cls.infill_pattern = 'soft_storey'
        else:
            cls.infill_pattern = 'oops'

        return cls

    @classmethod
    def from_riskue_name(cls, riskue_name):
        strsys_inf = riskue_name[2:len(riskue_name) - 2]
        if strsys_inf == '1':
            cls.structural_system = 'frame'
            cls.infill_pattern = 'bare'
        elif strsys_inf == '3.1':
            cls.structural_system = 'frame'
            cls.infill_pattern = 'infilled'
        elif strsys_inf == '3.2':
            cls.structural_system = 'frame'
            cls.infill_pattern = 'soft_storey'
        if strsys_inf == '4.1':
            cls.structural_system = 'dual'
            cls.infill_pattern = 'bare'
        elif strsys_inf == '4.2':
            cls.structural_system = 'dual'
            cls.infill_pattern = 'infilled'
        elif strsys_inf == '4.3':
            cls.structural_system = 'dual'
            cls.infill_pattern = 'soft_storey'
        else:
            cls.structural_system = 'oops'
            cls.infill_pattern = 'oops'

        cls.height_level = riskue_name[-2]
        cls.code_level = riskue_name[-1]

        return cls

    @staticmethod
    def get_riskue_height_level_from_storeys(storeys):
        _hl = ''
        if storeys <=3:
            _hl = 'L'
        elif storeys >=8:
            _hl = 'H'
        else:
            _hl = 'M'
        return _hl

    @staticmethod
    def get_riskue_design_level(code):
        _dl = ''
        if code == 'bd59':
            _dl = 'L'
        elif code == 'pa84':
            _dl = 'M'
        elif code == 'eak':
            _dl = 'H'
        else:
            _dl = 'N'
        return _dl


    @property
    def riskue_name(self) -> str:
        print('working!!!')
        tmp_code = 'RC'

        if self.structural_system == 'frame':
            if self.infill_pattern == 'infilled':
                tmp_code += '3.1'
            elif self.infill_pattern == 'soft_storey':
                tmp_code += '3.2'
            elif self.infill_pattern == 'bare':
                tmp_code += '1'

        elif self.structural_system == 'dual':
            if self.infill_pattern == 'infilled':
                tmp_code += '4.2'
            elif self.infill_pattern == 'soft_storey':
                tmp_code += '4.3'
            elif self.infill_pattern == 'bare':
                tmp_code += '4.1'

        tmp_code += self.get_riskue_height_level_from_storeys(self.storeys)
        tmp_code += self.get_riskue_design_level(self.code)

        return tmp_code

