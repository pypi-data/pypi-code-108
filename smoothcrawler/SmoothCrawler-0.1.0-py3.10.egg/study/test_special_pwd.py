from urllib.parse import quote_plus

db = "postgres"
user = "myuser"
db_host = "test:port"
app_db = "test_db"
url = f'{db}://{user}:%s@{db_host}/{app_db}' % quote_plus('u5876$&%*($&%')
print(url)
