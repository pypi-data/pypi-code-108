import jwt


class Token:
    def __init__(self, token):
        self.token = token
        self.dict = None

    def decode(self):
        if not self.dict:
            self.dict = jwt.decode(
                self.token, algorithms=["ES256"], options={"verify_signature": False}
            )
        return self.dict

    def hasRole(self, hasapp, hasrole):
        if "roles" not in self.decode():
            return False
        for app, role in self.decode()["roles"].items():
            if hasapp == app and hasrole == role:
                return True
        return False

    def getOrg(self):
        return self.decode()["org"]
