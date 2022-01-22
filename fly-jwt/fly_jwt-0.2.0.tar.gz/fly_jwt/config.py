import jwt


class _JWTConfig:
    def __init__(
        self,
        success_call=None,
        **kwargs
    ):
        self._configs = kwargs

        if success_call is not None and not callable(success_call):
            raise TypeError("success_call must be function.")
        self._success_call = success_call
        self.set_algorithm(kwargs.get("algorithm"))
        self._symmetric = self._is_symmetric()
        if not self._symmetric:
            self.set_pubkey(kwargs)
        else:
            if kwargs.get("public_key_path") or kwargs.get("public_key"):
                raise ValueError(f"\"{self.algorithm}\" don't use public key.")

        if self._symmetric:
            self.set_private_key(kwargs)
        self.set_fail_handler(kwargs.get("fail_handler"))
        self.set_auth_handler(kwargs.get("auth_handler"))

    def set_algorithm(self, algo):
        if algo is None:
            raise ValueError(
                f"which algorithm to use? {','.join(jwt.algorithms.get_default_algorithms().keys())}"
            )
        if not isinstance(algo, str):
            raise TypeError("algorithm must be str type.")

        if not algo in jwt.algorithms.get_default_algorithms():
            raise ValueError("invalid algorithm.")
        self._algorithm = algo

    @property
    def algorithm(self):
        return self._algorithm

    def set_pubkey(self, confs):
        public_key_path = confs.get("public_key_path")
        public_key = confs.get("public_key")
        if public_key_path is None and public_key is None:
            raise KeyError(f"\"{self._algorithm}\" must have public key.")
        elif public_key_path is not None and public_key is not None:
            raise KeyError(f"which use public key or public key path?")

        if public_key_path is not None and not isinstance(public_key_path, str):
            raise TypeError("public_key_path must be str type.")
        elif public_key is not None and not isinstance(public_key, str):
            raise TypeError("public_key must be str type.")

        if public_key is not None:
            self._public_key = public_key
        else:
            self._public_key_path = public_key_path
            with open(public_key_path, "r") as f:
                self._public_key = f.read()

    def set_private_key(self, confs):
        private_key = confs.get("private_key")
        private_key_path = confs.get("private_key_path")
        if private_key_path is None and private_key is None:
            raise KeyError(f"must have private key or private key path.")
        elif private_key_path is not None and private_key is not None:
            raise KeyError("which use private key or private key path?")

        if private_key is not None and not isinstance(private_key, str):
            raise TypeError("private_key must be str type.")
        if private_key_path is not None and not isinstance(private_key_path, str):
            raise TypeError("private_key_path must be str type.")

        if private_key is not None:
            self._private_key = private_key
        else:
            self._private_key_path = private_key_path
            with open(private_key_path, "r") as f:
                self._private_key = f.read()

    @property
    def private_key(self):
        return self._private_key

    @property
    def public_key(self):
        if not hasattr(self, "_public_key"):
            raise RuntimeError("no public key")
        return self._public_key

    def _is_symmetric(self):
        if getattr(self, "_algorithm") is None:
            raise AttributeError("must have algorithm property.")

        if self._algorithm in jwt.algorithms.requires_cryptography:
            # not need public key
            return False
        else:
            # need public key
            return True

    def set_fail_handler(self, handler):
        if handler is not None and not callable(handler):
            raise TypeError("fail handler must be callable object")
        self._fail_handler = handler

    @property
    def fail_handler(self):
        return self._fail_handler

    @property
    def success_handler(self):
        return self._success_call

    def set_auth_handler(self, handler):
        if handler is not None and not callable(handler):
            raise TypeError("auth_handler must be callable object")
        self._auth_handler = handler

    @property
    def auth_handler(self):
        return self._auth_handler
