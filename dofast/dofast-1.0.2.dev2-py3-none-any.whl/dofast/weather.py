import codefast as cf

from dofast.pipe import author


class Weather:
    def __init__(self):
        self.weather_api = 'http://t.weather.itboy.net/api/weather/city/101010100'

    def draw_weather_image(self):
        type_color_map = {
            '晴': 'forestgreen',
            '多云': 'gold',
            '阴': 'gold',
            '小雨': 'firebrick1',
            '阵雨': 'firebrick1',
            '中雨': 'firebrick2',
            '大雨': 'firebrick3',
            '暴雨': 'firebrick4',
            '霾': 'firebrick4'
        }
        data = self.r_data()
        cf.info('weather data requested.')
        text = '''digraph D{ graph [dpi=200]; aHtmlTable [shape=plaintext,label=<<table border='0' cellborder='1' CELLSPACING='0' CELLPADDING='4' style='rounded'>'''
        for e in data.items():
            k, v = e[0].upper(), e[-1]
            color = type_color_map.get(v)
            if color:
                text += f'<tr><td>{k}</td><td BGCOLOR="{color}">{v}</td></tr>'
            else:
                text += f'<tr><td>{k}</td><td>{v}</td></tr>'

        text += '''\n</table>>];}'''
        dot_file = '/tmp/weather.dot'
        cf.io.write(text, dot_file)
        cf.shell(f'dot -Tpng {dot_file} -o /tmp/weather.png')
        cf.io.rm(dot_file)

    def r_data(self):
        return cf.net.get(self.weather_api).json()['data']['forecast'][0]

    def _daily(self, markdown: bool = False):
        text = '\n'.join('| {} | {} |'.format(k, v)
                         for k, v in self.r_data().items())
        if markdown:
            text = '```|K|V|' + text
            text = text + '```'
        return text

    # @tg_bot(use_proxy=False)
    @cf.utils.retry(initial_wait=5)
    def daily(self):
        self.draw_weather_image()
        bot_token = author.get('VPSMONI714_BOT')
        cmd = f'curl -X POST "https://api.telegram.org/bot{bot_token}/sendPhoto?chat_id=@messalert" -F photo="@/tmp/weather.png"'
        cf.shell(cmd)


def entry():
    Weather().daily()


if __name__ == '__main__':
    wea = Weather()
    cf.say(wea.daily())
