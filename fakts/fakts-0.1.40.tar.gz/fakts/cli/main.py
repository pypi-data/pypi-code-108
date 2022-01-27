import asyncio
from fakts.beacon import EndpointBeacon, FaktsEndpoint
from rich.prompt import Prompt
import argparse




def main(name=None, url=None):
    if not name:
        name = Prompt.ask("How do you want this beacon to be advertisted as?", default="Arkitekt")

    if not url:
        url = Prompt.ask("Which Setup Uri do you want to advertise?", default="http://localhost:3000/setupapp")

    beacon = EndpointBeacon(advertised_endpoints= [FaktsEndpoint(url=url, name=name)])
    asyncio.run(beacon.run())


def entrypoint():
    parser = argparse.ArgumentParser(description = 'Say hello')
    parser.add_argument('--url', type=str, help='The Name of this script')
    parser.add_argument('--name', type=bool, help='Do you want to refresh')
    args = parser.parse_args()

    main(name=args.name, url=args.url)


if __name__ == "__main__":
    entrypoint()