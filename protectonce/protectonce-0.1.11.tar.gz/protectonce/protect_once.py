from . import core_interface
from .rules.rules_manager import RulesManager


def start():
    rules = core_interface.login()
    rules_manager = RulesManager(rules)
    rules_manager.apply_rules()


def stop():
    core_interface.stop()


start()
