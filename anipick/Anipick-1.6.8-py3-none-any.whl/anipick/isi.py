from rich.console import Console
import anipick
import argparse
import tabulate


def main():
    parse = argparse.ArgumentParser()
    parse.add_argument('-a', '--anime', metavar='title', help='get info of anime', nargs='+')
    parse.add_argument('-m', '--manga', metavar='title', help='get manga info', nargs='+')
    parse.add_argument('-ly', '--lyrics', metavar='keyword', help='get lyrics of the anime song', nargs='+')
    parse.add_argument('-s', '--song', help='usage: False/True')
    parse.add_argument('-tf', '--tablefmt', help='setting the table fmt')
    parse.add_argument('-q', '--quote',action='store_true' ,help='random quotes nime', required=False)
    parse.add_argument('-c', '--char', help='get character info', nargs='+')
    parse.add_argument('--author', action='version', version='Kenzawa/Babwa')
    parse.add_argument('-V', '--version', action='version', version='1.6.8')
    parse.add_argument('-nc', '--ncode', metavar='keyword', nargs='+', help='get ncode')
    parse.add_argument('-sn', '--seasonal', action='store_true', help='get title anime in specified seasonal')


    args = parse.parse_args()

    if args.anime:
        ' '.join(args.anime)
        title = anipick.Animegraphy(args.anime)
        name = title.title
        genre = title.genre
        eps = title.eps
        aired = title.aired
        studio = title.studio
        id = title.mal_id
        broadcast = title.broadcast
        adaptation = title.adaptation
        duration = title.duration
        nsfw = title.nsfw_scan()
        score = title.score
        rank = title.rank
        sequel = title.sequel
        status = title.status
        rated = title.rated
        try:
            op = title.op_song
            ed = title.ed_song
            op = op.split('#')[0:3]
            op = ', '.join(op)
            ed = ed.split('#')[0:3]
            ed = ', '.join(ed)
        except:
            op = 'Opening Song Not Found'
            ed = 'Ending Song Not Found'
        table = [['Anime', name], ['MAL ID', id], ['Status', status], ['Episode', eps], ['Aired', aired], ['Studio', studio],['Broadcast', broadcast], ['Duration', duration], ['NSFW', nsfw], [
        'Sequel', sequel], ['Score', score], ['RANK', rank], ['Genre', genre],['Adaptation', adaptation], ['Rated', rated]]
        try:
            if 'rue' in args.song:
                table = [['Anime', name], ['MAL ID', id], ['Status', status], ['Episode', eps], ['Aired', aired], ['Studio', studio],['Broadcast', broadcast], ['Duration', duration], ['NSFW', nsfw], [
            'Sequel', sequel], ['Score', score], ['RANK', rank], ['Genre', genre],['Adaptation', adaptation], ['Rated', rated], ['Opening', op], ['Ending', ed]]
            if 'lse' in args.song:
                table = [['Anime', name], ['MAL ID', id], ['Status', status], ['Episode', eps], ['Aired', aired], ['Studio', studio],['Broadcast', broadcast], ['Duration', duration], ['NSFW', nsfw], [
            'Sequel', sequel], ['Score', score], ['RANK', rank], ['Genre', genre],['Adaptation', adaptation], ['Rated', rated]]
        except:
            table = [['Anime', name], ['MAL ID', id], ['Status', status], ['Episode', eps], ['Aired', aired], ['Studio', studio],['Broadcast', broadcast], ['Duration', duration], ['NSFW', nsfw], [
        'Sequel', sequel], ['Score', score], ['RANK', rank], ['Genre', genre],['Adaptation', adaptation], ['Rated', rated]]
        if args.tablefmt:
            print(tabulate.tabulate(table, headers='firstrow', tablefmt=args.tablefmt))
        else:
            print(tabulate.tabulate(table, headers='firstrow'))
    if args.manga:
        ' '.join(args.manga)
        manga = anipick.Mangaography(args.manga)
        title = f'{manga.name} ({manga.name_jp})'
        aired = manga.aired
        genre = manga.genres
        author = manga.author
        status = manga.status
        publish = manga.is_publishing
        serialization = manga.serialization
        chapter = manga.chapter
        volume = manga.volume
        score = manga.score
        id = manga.manga_id
        related = manga.related
        table = [['Manga', title], ['MAL ID', id], ['Score', score], ['Publish', publish], ['Author', author], ['Status', status],
        ['Chapter', chapter], ['Volume', volume], ['Genre', genre], ['Related', related], ['Serialization', serialization], ['Aired', aired]]
        if args.tablefmt:
            print(tabulate.tabulate(table, headers='firstrow', tablefmt=args.tablefmt))
        else:
            print(tabulate.tabulate(table, headers='firstrow'))
    if args.quote:
            quotenime = anipick.Quotenime()
            anime = quotenime.anime
            quote = quotenime.quote
            char = quotenime.char
            table = [['Anime', anime], ['Character', char], ['Quotes', quote]]
            if args.tablefmt:
                print(tabulate.tabulate(table, headers='firstrow', tablefmt=args.tablefmt))
            else:
                print(tabulate.tabulate(table, headers='firstrow'))
    if args.lyrics:
        ' '.join(args.lyrics)
        query = anipick.Lyricspedia(args.lyrics)
        romaji = query.lyrics_romaji
        print(query.name ,romaji, sep='\n')

    if args.char:
        ' '.join(args.char)
        char = anipick.Charapedia(args.char)
        name = char.name
        nickname = char.nickname
        about = f'Height: {char.height}, Weight: {char.weight}, Birthday: {char.birthday}'
        id = char.mal_char_id
        animm = str(char.anime)
        animm = animm.replace(',', ',:').split(':')[0:5]
        animm = ', '.join(animm)
        mangaa = str(char.manga)
        mangaa = mangaa.replace(',', ',:').split(':')[0:5]
        mangaa = ', '.join(mangaa)
        table = [['Name', name], ['NickName', nickname], ['MAL CHAR ID', id], ['About:', about], ['Anime', animm], ['Manga', mangaa]]
        if args.tablefmt:
                print(tabulate.tabulate(table, headers='firstrow', tablefmt=args.tablefmt))
        else:
                print(tabulate.tabulate(table, headers='firstrow'))
    
    if args.ncode:
        ' '.join(args.ncode)
        code = anipick.HGEN('tobat_yuk_bang', query=args.ncode)
        print(code.nuclear)
    
    if args.seasonal:
        resultt = anipick.Seasonal(limit=5)
        table = [['Year', resultt.year], ['Season', resultt.season], ['anime', resultt.name]]
        if args.tablefmt:
                print(tabulate.tabulate(table, tablefmt=args.tablefmt))
        else:
                print(tabulate.tabulate(table))
if __name__ == '__main__':
    main()
