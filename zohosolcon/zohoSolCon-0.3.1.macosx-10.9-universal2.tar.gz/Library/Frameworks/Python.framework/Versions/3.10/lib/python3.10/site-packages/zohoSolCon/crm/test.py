import auth
import records
import related_list



client_id = "1000.0VNUXZ0W47OW228LHBAJZ7RFLC6T1O"
client_secret = "6920f0df429b5873910c4561dd9273b0344d1872cc"
grant = "1000.c7931eabcf1c014777d693f939fb7521.e3dc2c451c4a977ec3e0e6cb231b0178"

token = auth.Token(client_id=client_id, client_secret=client_secret, grant_token=grant)


token, response = records.get_records(token, "Accounts", page="1", per_page="1")

account_id = response[0]['id']

token, response = records.get_records(token, "Products", page="1", per_page="1")

prod_id = response[0]['id']

token, status, response = related_list.update_related_record(token, "Accounts", account_id, "Products", prod_id, {})

print(response)
