from protlib import CStruct, CInt

class JobParameterDescription(CStruct):
    name_offset = CInt()
    type = CInt()
    value_offset = CInt()

    def sizeof(self) -> int:
        return 12