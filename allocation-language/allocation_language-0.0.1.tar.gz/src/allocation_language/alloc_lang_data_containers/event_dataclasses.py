from dataclasses import dataclass

@dataclass
class EventData:
    data: dict
    scope_flag: bool = True
    aggregated: bool = False

    def __str__(self):
        string_rep = ''
        if (self.aggregated):
            string_rep += 'Aggregated: \n\t'
        string_rep += "Current Scope: " + ("Y" if self.scope_flag else "N") + ", "
        
        list_length = len(self.data.items())
        for i, (key, value) in enumerate(self.data.items()):
            if (type(value) == int):
                string_rep += f"{key}: {value:,d}"
            if (type(value) == float):
                string_rep += f"{key}: {value:,.2f}"
            if (type(value) == str):
                string_rep += f"{key}: {value!r}"
            
            if (i != list_length - 1):
                string_rep += ", "
        return string_rep

@dataclass
class AssessmentEvent:
    final_value: float | str

    def __str__(self):
        if (type(self.final_value) == str):
            return f"Assessment: {self.final_value!r}"
        if (type(self.final_value) == float):
            return f"Assessment: {self.final_value:,.2f}"