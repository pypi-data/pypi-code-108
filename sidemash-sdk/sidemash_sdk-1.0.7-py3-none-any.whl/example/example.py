from sidemash_sdk.Auth import Auth
from sidemash_sdk.Client import Client
from sidemash_sdk.StreamSquareSize import StreamSquareSize
from sidemash_sdk.UpdateStreamSquareForm import UpdateStreamSquareForm

auth = Auth(token= "1234", private_key= "****")
sdm = Client(auth)
s = StreamSquareSize
print(s)
print(s)
# form = UpdateStreamSquareForm
#    .by_id("01")
#    .remove_description()
#    .set_foreign_data("OK")
#    .set_is_elastic(True)
# sdm.stream_square().update(form)

#form = form.set_size(StreamSquareSize.S())

#sdm = Client(Auth(token="1234", private_key="****"))
#domain1 = sdm.domain.create(CreateDomainForm(name="ville-lille.com", purpose="Publish", description="My example domain name", foreign_data = None))
#domain2 = sdm.domain.getById("AZERTY")
#print(domain1)

# from sidemash_sdk.model.StreamSquare import StreamSquare
# from sidemash_sdk.form.CreateStreamSquareForm import CreateStreamSquareForm
# sdm.streamSquare.create(CreateStreamSquareForm(size=StreamSquare.Size.M, is_elastic=False))
