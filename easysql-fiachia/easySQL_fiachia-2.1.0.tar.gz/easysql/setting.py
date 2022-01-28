char_list = [
    "CHAR",
    "VARCHAR",
    "BINARY",
    "VARBINARY",
    "TINYBLOB",
    "BLOB",
    "MEDIUMBLOB",
    "LONGBLOB",
    "TINYTEXT",
    "TEXT",
    "MEDIUMTEXT",
    "LONGTEXT",
    "ENUM",
    "SET",

    "DATE",
    "TIME",
    "YEAR",
    "DATETIME",
    "TIMESTAMP",
]

int_list = [
    "TINYINT",
    "SMALLINT",
    "MEDIUMINT",
    "INTEGER",
    "INT",
    "BIGINT",

    "DECIMAL",
    "NUMERIC",

    "FLOAT",
    "DOUBLE",

    "BIT",
]

type_used_long_1 = [
    "BIT",
    "CHAR",
    "VARCHAR",
]
type_used_long_2 = [
    "DECIMAL",
    "NUMERIC",
]
type_unused_long = [
    "TINYINT",
    "SMALLINT",
    "MEDIUMINT",
    "INTEGER",
    "INT",
    "BIGINT",

    "FLOAT",
    "DOUBLE",

    "BINARY",
    "VARBINARY",
    "TINYBLOB",
    "BLOB",
    "MEDIUMBLOB",
    "LONGBLOB",
    "TINYTEXT",
    "TEXT",
    "MEDIUMTEXT",
    "LONGTEXT",
    "ENUM",
    "SET",

    "DATE",
    "TIME",
    "YEAR",
    "DATETIME",
    "TIMESTAMP",
]

mysql_type_to = {
    int: "INT",
    str: "VARCHAR",
    list: "VARCHAR",
    tuple: "VARCHAR",
    dict: "VARCHAR",
    bool: "BOOL",
    float: "DOUBLE",
}

database_table_engine = [
    "MEMORY",
    "MRG_MYISAM",
    "CSV",
    "FEDERATED",
    "PERFORMANCE_SCHEMA",
    "MyISAM",
    "InnoDB",
    "BLACKHOLE",
    "ARCHIVE"
]
database_table_charset = [
    "armscii8",
    "ascii",
    "big5",
    "binary",
    "cp1250",
    "cp1251",
    "cp1256",
    "cp1257",
    "cp850",
    "cp852",
    "cp866",
    "cp932",
    "dec8",
    "eucjpms",
    "euckr",
    "gb18030",
    "gb2312",
    "gbk",
    "geostd8",
    "greek",
    "hebrew",
    "hp8",
    "keybcs2",
    "koi8r",
    "koi8u",
    "latin1",
    "latin2",
    "latin5",
    "latin7",
    "macce",
    "macroman",
    "sjis",
    "swe7",
    "tis620",
    "ucs2",
    "ujis",
    "utf16",
    "utf16le",
    "utf32",
    "utf8",
    "utf8mb4",
]
