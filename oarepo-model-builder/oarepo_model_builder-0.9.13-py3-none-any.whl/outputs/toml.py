from tomlkit.exceptions import NonExistentKey

from oarepo_model_builder.outputs import OutputBase
import tomlkit, tomlkit.items


class TOMLOutput(OutputBase):
    TYPE = 'toml'

    def begin(self):
        try:
            with self.builder.filesystem.open(self.path) as f:
                self.original_data = f.read()
                self.toml = tomlkit.parse(self.original_data)
                self.parsed = tomlkit.dumps(self.toml, sort_keys=True)
        except FileNotFoundError:
            self.original_data = None
            self.toml = tomlkit.document()
            self.parsed = None

    @property
    def created(self):
        return self.original_data is None

    def table(self, key, key_type=tomlkit.items.KeyType.Bare):
        def get_by_key(key):
            _key = tomlkit.items.Key(key, key_type)
            try:
                return self.toml[_key]
            except KeyError:
                pass
            if '.' not in key:
                return None
            if '"' in key:
                key = [*key.split('"')[:2]]
            elif "'" in key:
                key = [*key.split("'")[:2]]
            else:
                key = [key, None]

            key_seq = [x for x in key[0].split('.') if x]
            if key[1]:
                key_seq.append(key[1])

            t = self.toml
            for k in key_seq:
                _key = tomlkit.items.Key(k, key_type)
                try:
                    t = t[_key]
                except KeyError:
                    return None
            return t

        t = get_by_key(key)
        if t is not None:
            return t
        t = tomlkit.table()
        self.toml.append(tomlkit.items.Key(key, key_type), t)
        return t

    def get(self, table, key):
        try:
            tbl = self.toml[table]
            return tbl[key]
        except NonExistentKey:
            return None

    def set(self, table, key, value, *others_key_values, key_type=tomlkit.items.KeyType.Bare):
        tbl = self.table(table)
        key = tomlkit.items.Key(key, key_type)
        tbl[key] = value
        while others_key_values:
            key = others_key_values[0]
            value = others_key_values[1]
            others_key_values = others_key_values[2:]

            key = tomlkit.items.Key(key, key_type)
            tbl[key] = value

    def setdefault(self, table, key, value, *others_key_values, key_type=tomlkit.items.KeyType.Bare):
        tbl = self.table(table)

        key = tomlkit.items.Key(key, key_type)
        tbl.setdefault(key, value)

        while others_key_values:
            key = others_key_values[0]
            value = others_key_values[1]
            others_key_values = others_key_values[2:]

            key = tomlkit.items.Key(key, key_type)
            tbl.setdefault(key, value)

    def finish(self):
        out = tomlkit.dumps(self.toml, sort_keys=True)
        if out != self.parsed:
            with self.builder.filesystem.open(self.path, 'w') as f:
                f.write(tomlkit.dumps(self.toml))
