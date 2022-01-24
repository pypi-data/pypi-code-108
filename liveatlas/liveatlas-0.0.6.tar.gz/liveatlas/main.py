from liveatlas.Server import Server


url = 'https://map.ccnetmc.com/nationsmap/standalone/dynmap_world.json?_=1641940944202'
# url = 'https://polis.datearth.com/standalone/dynmap_world.json?_=1642483579749'


def printTown(t):
    print('===============')
    print('Nation: ', t.nation)
    print('Occupied? ', t.occupied)
    print('Mayor: ', t.mayor)
    print('Peaceful? ', t.peaceful)
    print('Culture: ', t.culture)
    print('Board: ', t.board)
    print('Bank: ', t.bank)
    print('Upkeep: ', t.upkeep)
    print('Founded: ', t.founded)
    print('Resources: ', t.resources)
    print('Residents: ', t.residents)
    print('Population: ', t.residents_count)
    print('===============')


def main():
    server = Server(url)
    # towns = read_town_and_camp_data_from_json(make_request(url))[0]
    players = server.players
    for p in players:
        print(p.name)
        print(p.position)
        print(p.visible)
        print("-=-=-=-=-=-=-=-=-=-")
    # for t in towns:
    # printTown(t)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
