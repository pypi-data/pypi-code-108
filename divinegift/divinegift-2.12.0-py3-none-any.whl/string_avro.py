try:
    from confluent_kafka.avro import AvroProducer, AvroConsumer, SerializerError
except ImportError:
    pass


class StringAvroConsumer(AvroConsumer):
    def poll(self, timeout=None):
        """
        This is an overriden method from confluent_kafka.Consumer class. This handles message
        deserialization using avro schema

        :param float timeout: Poll timeout in seconds (default: indefinite)
        :returns: message object with deserialized key and value as dict objects
        :rtype: Message
        """
        if timeout is None:
            timeout = -1
        message = super(AvroConsumer, self).poll(timeout)
        if message is None:
            return None

        if not message.error():
            try:
                if message.value() is not None:
                    decoded_value = self._serializer.decode_message(message.value(), is_key=False)
                    message.set_value(decoded_value)
            except SerializerError as e:
                raise SerializerError("Message deserialization failed for message at {} [{}] offset {}: {}".format(
                    message.topic(),
                    message.partition(),
                    message.offset(),
                    e))
        return message
