from protlib import CStruct, CString, AUTOSIZED

class JobParameterData(CStruct):
    name = CString(length=AUTOSIZED)
    value = CString(length=AUTOSIZED)

    def sizeof(self) -> int:
        return len(self.name) + len(self.value) + 2