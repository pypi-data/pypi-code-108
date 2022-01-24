from tktl.future import Tktl

# instantiate client
client = Tktl()


# endpoints
@client.endpoint()
def func(x):
    return x
