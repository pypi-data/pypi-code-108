from dataclasses import dataclass


@dataclass(frozen=True)
class WorkGroup:
    name: str
    number: int = None
    type: str = None
    identifier: str = None
    prefix: str = None

    # to_hash -> dataclasses.asdict

    def to_xml(self, parent):
        parent.text = self.name
        for prop in ["number", "type", "identifier", "prefix"]:
            value = getattr(self, prop)
            if value:
                parent.attrib[prop] = str(value)
        return parent

    def to_asciibib(self, prefix=""):
        pref = f"{prefix}." if prefix else prefix
        out = [f"{pref}name:: {self.name}"]
        for prop in ["number", "type", "identifier", "prefix"]:
            value = getattr(self, prop)
            if value:
                out.append(f"{pref}{prop}:: {value}")
        return "\n".join(out)
