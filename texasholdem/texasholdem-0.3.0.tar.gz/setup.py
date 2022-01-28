# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['texasholdem',
 'texasholdem.card',
 'texasholdem.evaluator',
 'texasholdem.game',
 'texasholdem.gui']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'texasholdem',
    'version': '0.3.0',
    'description': 'A texasholdem python package',
    'long_description': '# texasholdem\nA python package for Texas Hold \'Em Poker.\n\n[Current Release Version v0.3.0](https://github.com/SirRender00/texasholdem/releases/tag/v0.3.0)\n\n[v1.0.0 Roadmap](https://github.com/SirRender00/texasholdem/wiki/Version-1.0.0-Roadmap)\n\n## Contributing\nTo be added as a contributor, please email me at evyn.machi@gmail.com with your GitHub username and mention one of the open issues / a new issue you would like to tackle first.\nFor more information about contributing, please see the wiki.\n\n## Install\n```bash\npip install texasholdem\n```\n\n## Quickstart Guide\nPlaying a game from the command line is as simple as the following:\n```python\nfrom texasholdem import TexasHoldEm\nfrom texasholdem.gui.text_gui import TextGUI\n\ngame = TexasHoldEm(buyin=500,\n                   big_blind=5,\n                   small_blind=2,\n                   max_players=6)\ngui = TextGUI()\ngui.set_player_ids(list(range(6)))      # see all cards\nwhile game.is_game_running():\n    game.start_hand()\n    while game.is_hand_running():\n        gui.print_state(game)\n\n        action, val = gui.accept_input()\n        while not game.validate_move(game.current_player, action, val):\n            print(f"{action} {val} is not valid for player {game.current_player}")\n            action, val = gui.accept_input()\n\n        gui.print_action(game.current_player, action, val)\n        game.take_action(action, val)\n```\n\n## Game Information\nGet game information and take actions through intuitive attributes:\n```python\nfrom texasholdem import TexasHoldEm, HandPhase, ActionType\n\ngame = TexasHoldEm(buyin=500, \n                   big_blind=5, \n                   small_blind=2,\n                   max_players=9)\ngame.start_hand()\n\nassert game.hand_phase == HandPhase.PREFLOP\nassert HandPhase.PREFLOP.next_phase() == HandPhase.FLOP\nassert game.chips_to_call(game.current_player) == game.big_blind\n\ngame.take_action(ActionType.CALL)\ngame.take_action(ActionType.RAISE, value=10)\n\nassert game.chips_to_call(game.current_player) == 10 - game.big_blind\n```\n\n## Card Module\nThe card module represents cards as 32-bit integers for simple and fast hand\nevaluations. For more information about the representation, see the `Card`\nmodule.\n\n```python\nfrom texasholdem.card import Card\n\ncard = Card("Kd")                       # King of Diamonds\nassert isinstance(card, int)            # True\nassert card.rank == 11                  # 2nd highest rank (0-12)\nassert card.pretty_string == "[ K ♦ ]"\n```\n\nThe `game.get_hand(player_id=...)` method of the `TexasHoldEm` class \nwill return a list of type `list[Card]`.\n\n## Evaluator Module\nThe evaluator module returns the rank of the best 5-card hand from a list of 5 to 7 cards.\nThe rank is a number from 1 (strongest) to 7462 (weakest). This determines the winner in the `TexasHoldEm` module:\n\n```python\nfrom texasholdem.card import Card\nfrom texasholdem.evaluator import evaluate, rank_to_string\n\nassert evaluate(cards=[Card("Kd"), Card("5d")],\n                board=[Card("Qd"), \n                       Card("6d"), \n                       Card("5s"), \n                       Card("2d"),\n                       Card("5h")]) == 927\nassert rank_to_string(927) == "Flush, King High"\n```\n\n## History Module\nExport and import the history of hands:\n```python\nfrom texasholdem.game.game import TexasHoldEm\nfrom texasholdem.gui.text_gui import TextGUI\n\ngame = TexasHoldEm(buyin=500, big_blind=5, small_blind=2)\ngame.start_hand()\n\nwhile game.is_hand_running():\n    game.take_action(*some_strategy(game))\n\n# export to file\ngame.export_history("./pgns/my_game.pgn")\n\n# import and replay\ngui = TextGUI()\nfor state in TexasHoldEm.import_history("./pgns/my_game.pgn"):\n    gui.print_state(state)\n```\n',
    'author': 'Evyn Machi',
    'author_email': 'evyn.machi@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/SirRender00/texasholdem',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
