from reahl.web.fw import ReahlWSGIApplication

application = ReahlWSGIApplication.from_directory(
    '/etc/reahl.d/prodigyhelmsman', start_on_first_request=True
)
