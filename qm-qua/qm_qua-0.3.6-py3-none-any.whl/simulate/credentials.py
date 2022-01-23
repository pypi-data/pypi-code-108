import grpc

# taken from https://github.com/grpc/grpc/tree/master/examples/python/auth

_SIGNATURE_HEADER_KEY = "x-signature"


class AuthGateway(grpc.AuthMetadataPlugin):
    def __call__(self, context, callback):
        """Implements authentication by passing metadata to a callback.
        Implementations of this method must not block.
        Args:
          context: An AuthMetadataContext providing information on the RPC that
            the plugin is being called to authenticate.
          callback: An AuthMetadataPluginCallback to be invoked either
            synchronously or asynchronously.
        """
        # Example AuthMetadataContext object:
        # AuthMetadataContext(
        #     service_url=u'https://localhost:50051/helloworld.Greeter',
        #     method_name=u'SayHello')
        signature = context.method_name[::-1]
        callback(((_SIGNATURE_HEADER_KEY, signature),), None)


def create_credentials():
    import certifi

    # Call credential object will be invoked for every single RPC
    call_credentials = grpc.metadata_call_credentials(
        AuthGateway(), name="auth gateway"
    )
    # Channel credential will be valid for the entire channel
    ROOT_CERTIFICATE = _load_credential_from_file(certifi.where())
    channel_credential = grpc.ssl_channel_credentials(ROOT_CERTIFICATE)
    # Combining channel credentials and call credentials together
    composite_credentials = grpc.composite_channel_credentials(
        channel_credential,
        call_credentials,
    )
    return composite_credentials


def _load_credential_from_file(filepath):
    with open(filepath, "rb") as f:
        return f.read()


__all__ = ["create_credentials"]
