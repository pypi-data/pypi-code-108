from pygments.formatters import HtmlFormatter
from pygments.style import Style
from pygments.token import Keyword, Name, Comment, String, Error, \
     Number, Operator, Generic

class OUStyle(Style):
    default_style = ""
    styles = {
        Keyword: '#a93812',
        Name: '#0b4586',
        Comment: '#008500',
        String: '#880c4d',
        Error: '#cd2041',
        Number: '#056876',
        Operator: '#a93812 bold',
        Generic: '',
    }


if __name__ == '__main__':
    print(HtmlFormatter(style=OUStyle).get_style_defs('.highlight'))
