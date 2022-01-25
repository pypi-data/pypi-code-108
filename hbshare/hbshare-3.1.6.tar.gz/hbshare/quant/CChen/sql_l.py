sql_quote = '''(
    `ID` bigint not null COMMENT \'主键\' AUTO_INCREMENT,
    `TDATE`  date not null COMMENT \'交易日期\',
    `EXCHANGE` varchar(255) COMMENT \'交易所代码\',
    `SYMBOL` varchar(255) COMMENT \'交易代码\',
    `LCLOSE` float COMMENT \'前收盘价(元)\',
    `OPEN` float COMMENT \'开盘价(元)\',
    `HIGH` float COMMENT \'最高价(元)\',
    `LOW` float COMMENT \'最低价(元)\',
    `CLOSE` float COMMENT \'收盘价(元)\',
    `VOLUME` bigint COMMENT \'成交量(股)\',
    `AMOUNT` bigint COMMENT \'成交金额(元)\',
    `AVGPRICE` float COMMENT \'当日成交均价(元)\',
    `CHG` float COMMENT \'涨跌金额(元)\', 
    `PCHG` float COMMENT \'涨跌幅(%)\', 
    `PRANGE` float COMMENT \'振幅(%)\', 
    `MCAP` bigint COMMENT \'流通市值(元)\', 
    `TCAP` bigint COMMENT \'总市值(元)\', 
    primary key (`ID`)
    )
    '''