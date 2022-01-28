class __Attribute_Type:
    def __init__(self, *args):
        for __arg_i in args:
            self.__setattr__(str(__arg_i), __arg_i)
        pass


class __Engine:
    def __init__(self):
        self.MEMORY = "MEMORY"
        self.MRG_MYISAM = "MRG_MYISAM"
        self.CSV = "CSV"
        self.FEDERATED = "FEDERATED"
        self.PERFORMANCE_SCHEMA = "PERFORMANCE_SCHEMA"
        self.MyISAM = "MyISAM"
        self.InnoDB = "InnoDB"
        self.BLACKHOLE = "BLACKHOLE"
        self.ARCHIVE = "ARCHIVE"


class __Charset:
    def __init__(self):
        self.armscii8 = "armscii8"
        self.ascii = "ascii"
        self.big5 = "big5"
        self.binary = "binary"
        self.cp1250 = "cp1250"
        self.cp1251 = "cp1251"
        self.cp1256 = "cp1256"
        self.cp1257 = "cp1257"
        self.cp850 = "cp850"
        self.cp852 = "cp852"
        self.cp866 = "cp866"
        self.cp932 = "cp932"
        self.dec8 = "dec8"
        self.eucjpms = "eucjpms"
        self.euckr = "euckr"
        self.gb18030 = "gb18030"
        self.gb2312 = "gb2312"
        self.gbk = "gbk"
        self.geostd8 = "geostd8"
        self.greek = "greek"
        self.hebrew = "hebrew"
        self.hp8 = "hp8"
        self.keybcs2 = "keybcs2"
        self.koi8r = "koi8r"
        self.koi8u = "koi8u"
        self.latin1 = "latin1"
        self.latin2 = "latin2"
        self.latin5 = "latin5"
        self.latin7 = "latin7"
        self.macce = "macce"
        self.macroman = "macroman"
        self.sjis = "sjis"
        self.swe7 = "swe7"
        self.tis620 = "tis620"
        self.ucs2 = "ucs2"
        self.ujis = "ujis"
        self.utf16 = "utf16"
        self.utf16le = "utf16le"
        self.utf32 = "utf32"
        self.utf8 = "utf8"
        self.utf8mb4 = "utf8mb4"


class __DataStructure:
    def __init__(self):
        self.TINYINT = "TINYINT"
        self.SMALLINT = "SMALLINT"
        self.MEDIUMINT = "MEDIUMINT"
        self.INTEGER = "INTEGER"
        self.INT = "INT"
        self.BIGINT = "BIGINT"

        self.DECIMAL = "DECIMAL"
        self.NUMERIC = "NUMERIC"

        self.FLOAT = "FLOAT"
        self.DOUBLE = "DOUBLE"

        self.BIT = "BIT"

        self.DATE = "DATE"
        self.TIME = "TIME"
        self.YEAR = "YEAR"
        self.DATETIME = "DATETIME"
        self.TIMESTAMP = "TIMESTAMP"

        self.CHAR = "CHAR"
        self.VARCHAR = "VARCHAR"
        self.BINARY = "BINARY"
        self.VARBINARY = "VARBINARY"
        self.TINYBLOB = "TINYBLOB"
        self.BLOB = "BLOB"
        self.MEDIUMBLOB = "MEDIUMBLOB"
        self.LONGBLOB = "LONGBLOB"
        self.TINYTEXT = "TINYTEXT"
        self.TEXT = "TEXT"
        self.MEDIUMTEXT = "MEDIUMTEXT"
        self.LONGTEXT = "LONGTEXT"
        self.ENUM = "ENUM"
        self.SET = "SET"

    def DECIMAL(self, accuracy, scale):
        return "DECIMAL(%s,%s)" % (accuracy, scale)

    def NUMERIC(self, accuracy, scale):
        return "NUMERIC(%s,%s)" % (accuracy, scale)

    def BIT(self, figure):
        return "BIT(%s)" % figure

    def CHAR(self, figure):
        return "CHAR(%s)" % figure

    def VARCHAR(self, figure):
        return "VARCHAR(%s)" % figure


Engine = __Engine()
Charset = __Charset()
DataStructure = __DataStructure()






