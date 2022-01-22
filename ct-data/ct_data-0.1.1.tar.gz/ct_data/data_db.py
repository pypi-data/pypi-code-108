""" this is just a file to house the data db structure"""

# finance section
# accounts table is always created first
account_type_options = ['file', 'api']
accounts = """ CREATE TABLE IF NOT EXISTS accounts (
                            acc_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            num INTEGER NOT NULL UNIQUE,
                            institution TEXT,
                            desc TEXT,
                            filepath TEXT NOT NULL,
                            source TEXT CHECK(source IN ('file', 'api')),
                            adjust REAL
    
                        ); """

categories = """ CREATE TABLE IF NOT EXISTS categories (
                            cat_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            cat_desc TEXT NOT NULL
    
                        ); """

transactions = """ CREATE TABLE IF NOT EXISTS transactions (
                            trans_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            date DATETIME NOT NULL,
                            desc TEXT NOT NULL,
                            amount REAL NOT NULL,
                            total_id REAL NOT NULL,
                            
                            processed INTEGER CHECK(processed IN (0,1)) DEFAULT(0),
                            
                            cat_id INTEGER DEFAULT NULL,
                            acc_id INTEGER,
                            FOREIGN KEY (cat_id) REFERENCES categories (cat_id) ON DELETE SET NULL ON UPDATE CASCADE,
                            FOREIGN KEY (acc_id) REFERENCES accounts (acc_id) ON DELETE CASCADE ON UPDATE CASCADE
                            
                        ); """

tags = """ CREATE TABLE IF NOT EXISTS tags (
                            tag_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            desc TEXT NOT NULL UNIQUE
    
                        ); """

tags_links = """ CREATE TABLE IF NOT EXISTS tags_links (
                            trans_id INTEGER,
                            tag_id INTEGER,
                            UNIQUE(trans_id, tag_id)
                            FOREIGN KEY (trans_id) REFERENCES transactions (trans_id) ON DELETE CASCADE ON UPDATE CASCADE,
                            FOREIGN KEY (tag_id) REFERENCES tags (tag_id) ON DELETE CASCADE ON UPDATE CASCADE
    
                        ); """

# create slits to store originals of split transactions so they arent replicated in updates
splits = """ CREATE TABLE IF NOT EXISTS splits (
                            trans_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            date DATETIME NOT NULL,
                            desc TEXT NOT NULL,
                            amount REAL NOT NULL,
                            total_id REAL NOT NULL
                            
                        ); """

crypto = """ CREATE TABLE IF NOT EXISTS crypto (
                            cr_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            date DATETIME DEFAULT CURRENT_TIMESTAMP,
                            desc TEXT NOT NULL,
                            qty REAL NOT NULL,
                            price REAL NOT NULL,
                            total REAL NOT NULL
                            
                        ); """

crypto_holdings = """ CREATE TABLE IF NOT EXISTS crypto_holdings (
                            crh_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            desc TEXT NOT NULL,
                            symbol TEXT NOT NULL,
                            parent_chain TEXT,
                            chain_address TEXT
                            
                        ); """

qtrade = """ CREATE TABLE IF NOT EXISTS qtrade (
                            qt_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            date DATETIME DEFAULT CURRENT_TIMESTAMP,
                            symbol TEXT NOT NULL,
                            symbolId TEXT NOT NULL,
                            openQuantity INTEGER,
                            closeQuantity INTEGER,
                            currentMarketValue REAL NOT NULL,
                            currentPrice REAL NOT NULL,
                            averageEntryPrice REAL NOT NULL,
                            totalCost REAL NOT NULL
                            
                        ); """

FINANCE_TABLES = [accounts, categories, transactions, tags, tags_links, splits, crypto, crypto_holdings, qtrade]