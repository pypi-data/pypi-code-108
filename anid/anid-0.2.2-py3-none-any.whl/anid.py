import json
import sys

import click
import requests

from anid.downloader import download_file


@click.command()
@click.argument('anime', required=True)
@click.option('-e', '--episodes',
              required=True, type=int, help='Number of episodes')
@click.option('-s', '--start',
              required=False, type=int, default=1, help='Number of episodes')
def anid(anime: str, episodes: int, start: int = 1):
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"
    }
    base_url = 'https://animefire.net/video/{anime}/{episode}'

    for i in range(start, episodes+1):
        url = base_url.format(anime=anime, episode=i)
        print(url)

        try:
            response = requests.get(url, headers=headers)
        except ConnectionError:
            click.echo('Connection error! Check your connection')
            sys.exit(1)

        if response.ok:
            content = json.loads(response.content)
            if content['response']['status'] == '200':
                download_url = get_url_download(content['data'])
                file_name = f'{anime}-{i}.mp4'
                download_file(download_url, file_name)
                click.echo('')

            else:
                print(content['response']['text'])

        else:
            click.echo(response.status_code)
            click.echo(response.content)
            sys.exit(1)


def get_url_download(data: dict):
    """ Check Resolutions and return episode url """
    for src in data:
        if src['label'] == '720p':
            click.echo('Resolution 720p found!')
            return src['src']
    for src in data:
        if src['label'] == '360p':
            click.echo('Resolution 360p found')
            return src['src']

    click.secho('Resolutions 720p or 360p not found!', bold=True)
    click.echo('Resolutions avaliable:')
    for i in data:
        click.echo(i['label'])
    sys.exit(1)


if __name__ == '__main__':
    anid()
