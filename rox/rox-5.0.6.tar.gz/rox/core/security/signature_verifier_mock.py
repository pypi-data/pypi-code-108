class SignatureVerifierMock:
    def verify(self, data, signature_base64):
        return True
