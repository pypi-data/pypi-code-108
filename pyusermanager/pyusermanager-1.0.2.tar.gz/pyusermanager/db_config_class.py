class DB_Config():

    def __init__(self,provider = "mysql", host = "127.0.0.1",port = 3306, user = "testuser", pw = "testpassword", db_name = "user"):
        self.provider = provider
        self.host       = host
        self.port       = port
        self.user       = user
        self.pw         = pw
        self.db_name    = db_name


    def __str__(self):
        return f"""
=============DB-Config=============

    provider:   {self.provider}
    host:       {self.host}
    port:       {self.port}
    user:       {self.user}
    password:   {self.pw}      
    db_name:    {self.db_name}
    
===================================
        """