class StreamController:
    """
    Class for managing interaction with the /stream endpoints
    """
    def __init__(self, client):
        """
        Constructor, must be instantiated with a client to provide auth support
        :param client: (Client) client object
        """
        self.client = client

    def create_stream(self, stream_display_name):
        """
        Creates a new Stream
        :param stream_display_name: (String) Desired Display name of new stream
        :return: (Requests Response) Response from API call, Body of response is a Stream Object
        """
        request_body = {'displayName': stream_display_name}
        return self.client.call_api('POST',
                                    "/stream",
                                    body=request_body)

    def get_stream(self, stream_id):
        """
        Gets the details of a stream
        :param stream_id: (String) Stream ID
        :return: (Requests Response) Response from API call, Body of response is a Stream Object
        """
        return self.client.call_api('GET',
                                    f"/stream/{stream_id}")

    def delete_stream(self, stream_id):
        """
        Deletes a Stream
        :param stream_id: (String) Stream ID
        :return: (Requests Response) Response from API call, Body of response is a Stream Object
        """
        return self.client.call_api('DELETE',
                                    f"/stream/{stream_id}")

    def add_new_machine_client_to_stream(self, stream_id, client_display_name,
                                         is_producer=False, is_consumer=False):
        """
        Creates a new Client ID, and grants that client permissions on a Stream
        :param stream_id: (String) Stream ID to add the client to
        :param client_display_name: (String) Desired display name of the client
        :param is_producer:  (Boolean) Should producer access be granted to this Client
        :param is_consumer: (Boolean) Should consumer access be granted to this Client
        :return: (Requests Response) Response from API call, Body of response is a Stream Object
        """
        body = {'actorDisplayName': client_display_name,
                'isProducer': is_producer,
                'isConsumer': is_consumer,
                'actorType': 'CLIENT'
                }
        return self.client.call_api('POST',
                                    f"/stream/{stream_id}/permissions",
                                    body=body)

    def add_public_client_to_stream(self, stream_id, client_display_name,
                                         is_producer=False, is_consumer=False):
        """
        Creates a new Client ID, and grants that client permissions on a Stream
        :param stream_id: (String) Stream ID to add the client to
        :param client_display_name: (String) Desired display name of the client
        :param is_producer:  (Boolean) Should producer access be granted to this Client
        :param is_consumer: (Boolean) Should consumer access be granted to this Client
        :return: (Requests Response) Response from API call, Body of response is a Stream Object
        """
        body = {'actorDisplayName': client_display_name,
                'isProducer': is_producer,
                'isConsumer': is_consumer,
                'actorType': 'PUBLIC'
                }
        return self.client.call_api('POST',
                                    f"/stream/{stream_id}/permissions",
                                    body=body)

    def add_user_to_stream(self, stream_id, user_email, is_producer=False, is_consumer=False):
        """
        Adds a human user to a stream with permissions
        :param stream_id:  (String) Stream ID to add the User to
        :param user_email: (String) The Email address of the User to Add
        :param is_producer: (Boolean) Should producer access be granted to this User
        :param is_consumer: (Boolean) Should consumer access be granted to this User
        :return: (Requests Response) Response from API call, Body of response is a Stream Object
        """
        body = {'actorDisplayName': user_email,
                'isProducer': is_producer,
                'isConsumer': is_consumer,
                'actorType': 'USER'
                }
        return self.client.call_api('POST',
                                    f"/stream/{stream_id}/permissions",
                                    body=body)

    def remove_machine_client_from_stream(self, stream_id, client_id):
        """
        Removes access from a client on a given stream
        :param stream_id: (String) Stream ID to remove client from
        :param client_id: (String) Client ID to remove from Stream
        :return: (Requests Response) Response from API call, Body of response is a Stream Object
        """
        body = {'actorId': client_id,
                'actorType': 'CLIENT'
                }
        return self.client.call_api('DELETE',
                                    f"/stream/{stream_id}/permissions",
                                    body=body)

    def remove_user_from_stream(self, stream_id, user_id):
        """
        Removes access from a client on a given stream
        :param stream_id: (String) Stream ID to remove client from
        :param user_id: (String) User ID to remove from Stream
        :return: (Requests Response) Response from API call, Body of response is a Stream Object
        """
        body = {'actorId': user_id,
                'actorType': 'USER'
                }
        return self.client.call_api('DELETE',
                                    f"/stream/{stream_id}/permissions",
                                    body=body)
