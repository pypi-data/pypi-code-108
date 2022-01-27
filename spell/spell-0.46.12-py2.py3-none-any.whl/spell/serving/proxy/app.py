from spell.serving.proxy import make_app

# Hypercorn will import this global variable
app = make_app()
