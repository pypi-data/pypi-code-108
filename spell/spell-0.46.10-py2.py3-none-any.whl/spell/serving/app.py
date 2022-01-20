from spell.serving import server
from spell.serving import settings


app = server.make_app(debug=settings.DEBUG)
