import abc

from whizbang.domain.menu.command_menu import CommandMenu

from whizbang.domain.models.menu.menu_command_list import MenuCommandList

title = r"""

                                         /\\
                                        /  \\
                                       |    |
                                     --:'''':--
                                       :'_' :
                                       _:"":\___
                        ' '      ____.' :::     '._
                       . *=====<<=)           \    :
                        .  '      '-'-'\_      /'._.'
                                         \====:_ ""
                                        .'     \\
      ,. _                        whiz :       :                   
    '-'    ).                         /   :    \\
  (        '  )                       :   .      '.
 ( -  .bang.  - _                     :  : :      :
(    .'  _ )     )                    :__:-:__.;--'
'-  ()_.\,\,   - deployer             '-'   '-'
"""


class IMenuInvoker(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def __build_menu(self):
        """"""

    @abc.abstractmethod
    def display_menu(self):
        """"""


class MenuInvoker:
    def __init__(self, menu_command_list: MenuCommandList):
        self._menu_command_list = menu_command_list.command_list
        self._menu_title = title

    def __build_menu(self):
        menu = CommandMenu(title=title, options=self._menu_command_list)
        return menu

    def display_menu(self):
        menu = self.__build_menu()
        menu.open_menu()
