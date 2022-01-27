from http.server import SimpleHTTPRequestHandler
from .state_storage import StateStorage

state_storage = StateStorage()


class HealthCheck(SimpleHTTPRequestHandler):
    def do_GET(self):
        http_response = 418

        if state_storage.get_ready_state():
            http_response = 200

        self.send_response(http_response)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        return