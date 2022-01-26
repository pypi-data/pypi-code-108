import requests
import datetime
from slugify import slugify


class TeamClient(object):

    def __init__(self, api_url, team_name):
        self.api_url = api_url
        self.team_name = team_name

    def slugify(self, name):
        return slugify(
            name,
            regex_pattern=r'[^\w\S-]'
        )

    @property
    def team(self):
        if not self.api_url:
            raise Exception('Team API URL not informed.')
        if not self.team_name:
            raise Exception('Team name not informed.')
        slugify_name = self.slugify(self.team_name)
        url = '{}/slug/{}'.format(self.api_url, slugify_name)
        res = requests.get(url)
        if res.ok:
            return res.json()
        error = 'Team {} not found.'.format(self.team_name)
        raise Exception(error)

    @property
    def team_id(self):
        return self.team.get('id')

    def make_labels(self, engine_name='', infra_name='', database_name=''):

        team = self.team

        labels = {
            'servico_de_negocio': team.get('servico-de-negocio'),
            'cliente': team.get('cliente'),
            'team_slug_name': team.get('slug'),
            'team_id': team.get('id'),
            'create_at': datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S'),
            'engine': engine_name,
            'infra_name': infra_name,
            'database_name': database_name,
            'origin': 'dbaas'
        }

        return labels
