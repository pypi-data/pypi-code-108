import os

from niota.chrysalis import IotaClient
from niota.signature import generate_key_pair


'''
Create a testing environment the same as Storage Backend.

Storage Backend does not use niota currently. The goal of this script is to
create a minimum environment for testing niota for Storage Backend
in the future:

    1. Ensure Storage Backend IOTA works here. (done)
    2. Ensure niota works here.
    3. Ensure niota to be compatible or with minimal effort for integration.

utils/{iota_chrysalis, signature}.py are copied from Storage Backend
without any change.

Usage
    $ python3 utils/hello_iota_storage_backend.py
'''

Mainnet_explorer = 'https://explorer.iota.org/mainnet'


def main():
    private_key, public_key = generate_key_pair()
    iota = IotaClient(private_key, public_key)

    raw_cid = 'bafybeifk6fyfmrgylejsujeido7kob7ysp6353wb5b7i5nhc64kzkxdvs4'
    service_message = 'hello world'
    message_id, index = iota.create_message(
        raw_cid=raw_cid,
        provider='HelloProtocol',
        service_message=service_message,
    )

    print('Message ID:', message_id)
    print('Message URL:', os.path.join(Mainnet_explorer, 'message', message_id))
    print('Index:', index)

    message_data = iota.get_message_data(message_id)
    iota.verify_message_data(message_data)
    print('Message verified successfully')


if __name__ == '__main__':
    main()
