from markupsafe import escape


class BaseFrontendApplicationTest(object):
    def get_flash_messages(self):
        with self.client.session_transaction() as session:
            return tuple((category, escape(message)) for category, message in (session.get("_flashes") or ()))
