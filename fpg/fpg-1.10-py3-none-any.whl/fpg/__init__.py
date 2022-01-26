################################################################################
# Flexible PostgreSQL Client
################################################################################
import re, pg8000.native

__all__ = ['pgdb']

# db = pgdb('user@password:host:port/dbname')
# db = pgdb({host = '...', port = 1234, ...})
# db = pgdb(spec, verbose = True, dry = True)
class pgdb:
    @staticmethod
    def parse_url(url):
        ret = {}
        mo = re.match(r'^\w+://(.+)$', url)
        if mo:
            url = mo.group(1)
        i = url.rfind('@')
        if i >= 0:
            auth = url[:i]
            url = url[i+1:]
            j = auth.find(':')
            if j < 0:
                ret['user'] = auth
            else:
                ret['user'] = auth[:j]
                ret['password'] = auth[j+1:]
        mo = re.match(r'^([^:/]+)(:(\d+))?(/(.+))?$', url)
        if mo is not None:
            host, port, path = (mo.group(1), mo.group(3), mo.group(5))
            ret['host'] = host
            if port is not None:
                try:
                    ret['port'] = int(port)
                except ValueError:
                    ret['port'] = port
            if path is not None:
                ret['database'] = path
        return ret

    @staticmethod
    def parse_range(spec, sep = '-'):
        ret = spec.split(sep)
        if (len(ret) == 1):
            return [spec, spec]
        if (len(ret) > 2):
            return ret[1:2]
        if (len(ret) == 2):
            beg, end = ret
            if len(beg) > len(end):
                ret = [beg, beg[0:(len(beg)-len(end))] + end]
        return ret

    @staticmethod
    def dstr(spec):
        if type(spec) is str:
            return spec
        if type(spec) is int:
            return str(spec)
        return spec.strftime('%Y%m%d')

    def __init__(self, spec, **kw):
        if type(spec) is bytes:
            spec = spec.decode('utf-8')
        if type(spec) is not str:
            raise ValueError('Bad spec type %s' % type(spec))
        self.conn    = None
        self.spec    = pgdb.parse_url(spec)
        self.verbose = kw.get('verbose', False)
        self.dry     = kw.get('dry', False)

    def __del__(self):
        self.close()

    # lazy connection
    def run(self, sql):
        if self.conn is None:
            self.conn = pg8000.native.Connection(**self.spec)
        return self.conn.run(sql)

    def close(self):
        if self.conn is not None:
            self.conn.close()

    # this function is quite tricky (and powerful), sql can be:
    # - (format, arg1, arg2, ...)
    # - (sql)
    # - sql
    def execute(self, sql):
        if not sql:
            raise ValueError('cannot execute empty SQL')
        if type(sql) is tuple:
            sql = (sql[0] % sql[1:]) if len(sql) > 1 else sql[0]

        # echo SQL
        if self.verbose:
            if type(sql) is list:
                for x in sql:
                    print(f'[fpg-exec] {x}')
            else:
                print(f'[fpg-exec] {sql}')
        return None if self.dry else self.run(sql)

    def __call__(self, *sql):
        return self.execute(sql)

    def row(self, *sql):
        rows = self.execute(sql)
        return rows[0] if self.conn.row_count else None

    def col(self, *sql):
        return [row[0] for row in self.execute(sql)]

    def cols(self, *sql):
        rows = self.execute(sql)
        if not self.conn.row_count:
            return []
        ret = [[]] * self.conn.row_count
        for i in range(len(rows[0])):
            ret[i] = [r[i] for r in rows]
        return ret

    def val(self, *sql):
        rows = self.execute(sql)
        return rows[0][0] if self.conn.row_count else None

    def last(self, *sql):
        rows = self.execute(sql)
        return self.execute(sql)[-1][0] if self.conn.row_count else None

    def bounds(self, *sql):
        rows = self.execute(sql)
        if not self.conn.row_count:
            return ()
        return (rows[0][0], rows[-1][0])

    def dict(self, *sql):
        rows = self.execute(sql)
        if not self.conn.row_count or len(rows[0]) < 2:
            return {}
        if len(rows[0]) == 2:
            return {r[0]: r[1] for r in rows}
        return {r[0]: r[1:] for r in rows}

    def mdict(self, *sql):
        rows = self.execute(sql)
        if not self.conn.row_count or len(rows[0]) < 2:
            return {}
        single = len(rows[0]) == 2
        ret = {}
        for row in rows:
            key = row[0]
            val = row[1] if single else row[1:]
            if key not in ret:
                ret[key] = []
            ret[key].append(val)
        return ret

### fpg/__init__.py ends here
