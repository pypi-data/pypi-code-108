# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['kinopoisk',
 'kinopoisk.data',
 'kinopoisk.data.movie',
 'kinopoisk.data.movie.tv_series',
 'kinopoisk.errors',
 'kinopoisk.utils']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.8.1,<4.0.0']

setup_kwargs = {
    'name': 'kinopoisk-unofficial-api',
    'version': '0.6.3',
    'description': 'Simple wrapper of kinopoiskapiunofficial.tech',
    'long_description': '# kinopoisk unofficial API\n\nThis is simple python package for getting data from [unofficial kinopoisk API](https://kinopoiskapiunofficial.tech).\n\n## Installing\n\n**pip**\n\n```bash\npip install kinopoisk-unofficial-api\n```\n\n**poetry**\n\n```bash\npoetry add kinopoisk-unofficial-api\n```\n\n## Getting token\n\nWhy this not work. What the token and why this require it from me?\nFor interact to [API](https://kinopoiskapiunofficial.tech) you should getting api token. That get it you need sign up to [their site](https://kinopoiskapiunofficial.tech/signup). After register go to profile and save your token somewhere.\n\n## How to use\n\nFor begin you should create the **KPClient** instance.\n\n```python\nfrom kinopoisk import KPClient\n\nclient = KPClient(<your token>)\n```\n\nWhen you have client you can used all functional this library.\n\n### Getting movie\n\n```python\nmatrix = await client.get_movie_data(301)\nprint(matrix)\n```\n\nYou can get e.g. name, release date, raiting, length of this movie and more.\n\n```python\nmatrix.name.en\n\'The Matrix\'\nmatrix.year\n1999\nmatrix.length\n136\n```\n\nIf you not know movie id (that to be often) may use another method named ***search_movie***\n\n```python\nanswer = await client.search_movie(\'Mr. Robot\')\nmr_robot = answer[0] # If you search popular movie, that usually this movie should be to first\n```\n\n### Getting data of movie\nIn previous example we got tv series. By default it take without it seasons. That load it you should get it id and call to method of client  ***get_seasons_data***\n\n```python\nseasons = await client.get_seasons_data(mr_robot.id.kinopoisk)\nfor season in seasons:\n\tprint(season.episodes)\n```\n\nYet this not exactly conveniently. Store seasons and it tv series between it may be not good idea. So that, you may not splitting data, for it need call tv series method ***load_seasons***.\n\n```python\nawait mr_robot.load_seasons(client)\nfor season in mr_robot.seasons:\n    print(season.episodes)\n# Or just\nfor season in mr_robot:\n    print(season.episodes)\n```\n\nSeason have a episodes (Seriously?) that may be get it same way.\n\n```python\nfor season in mr_robot:\n    for episode in season:\n        print(episode.name.en)\n\t\t# First episode named \'eps1.0_hellofriend.mov\'\n```\n\n### Getting facts and bloopers of movie\n\n```python\nfor fact in await client.get_facts(mr_robot.id.kinopoisk):\n\tprint(fact.text)\n```\n\n### Getting persons\n\n```python\nbc = (await client.search_person(\'Benedict Cumberbatch\'))[0]\nawait bc.get_all_data(client)\nprint(bc.birthday.strftime("%d %B, %Y"))\n# Output 19 July, 1976\n```\n\nOr you can get persons of some movie\n\n```python\npersons = await mr_robot.get_persons(client)\nactors = []\nfor person in persons:\n    if person.is_actor:\n        actors.append(person)\nfor actor in actors[:10]: print(f\'{actor.name.en}: {actor.character}\')\n```\n\n### Getting reviews\n\n```python\nreviews = await mr_robot.get_reviews(client)\nfor review in reviews: print(f\'{review.author} - {review.title}:\\n{review.text}\')\n```\n\n### Getting similars movies\n\n```python\nmovies = await mr_robot.get_similars(client)\nfor movie in movies:\n    print(movie.name.en)\n```\n\n```\nFight Club\nWho Am I - Kein System ist sicher\nThe Matrix\nDexter\nA Beautiful Mind\nHackers\nThe Social Network\nThe Fifth Estate\nV for Vendetta\nBlack Mirror\n23\n```\n\n### Getting images\n\nYou can get different images e.g. posters wallpapers, backstage photo and more\n\n```python\nimages = await mr_robot.get_images(client, ImageTypes.poster)\nfor image in images:\n    print(image.big)\n```\n\n<p style="display: flex;">\n\t<img height=250 src="https://avatars.mds.yandex.net/get-kinopoisk-image/1704946/981bdebd-d27d-4ea4-85eb-9c51c0bd678b/orig" />\n\t<img height=250 src="https://avatars.mds.yandex.net/get-kinopoisk-image/1704946/cc2adcad-a448-42b1-a329-c6c222b047af/orig" /> \n\t<img height=250 src="https://avatars.mds.yandex.net/get-kinopoisk-image/1900788/f69aae71-cb44-432e-aaf5-657e551b018d/orig" />\n\t<img height=250 src="https://avatars.mds.yandex.net/get-kinopoisk-image/1898899/49853c24-b2b2-4698-9b3a-74e6ef0e37b6/orig">\n</p>\n### Getting some tops\n\n**Best 250**\n\n```python\nfor movie in (await client.get_top(TopTypes.best_250))[:5]:\n\tprint(movie.name.en)\n```\n\n**Popular 100**\n\n```python\nfor movie in (await client.get_top(TopTypes.popular_100))[:5]:\n\tprint(movie.name.en)\n```\n\n**Future**\n\n```python\nfor movie in (await client.get_top(TopTypes.best_250))[:5]:\n\tprint(movie.name.en)\n```\n\n',
    'author': 'Nawot',
    'author_email': 'Nawot001@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Nawot/kinopoisk-unofficial-api',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
