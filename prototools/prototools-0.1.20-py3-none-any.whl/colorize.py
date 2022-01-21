import os

os.system("")

RESET = '0'
colors = (
    "black",
    "red",
    "green",
    "yellow",
    "blue",
    "magenta",
    "cyan",
    "white",
)
opt_dict = {
    'bold': '1', 
    'underscore': '4', 
    'blink': '5', 
    'reverse': '7', 
    'conceal': '8'
}
fg ={colors[x]: f'3{x}' for x in range(8)}
bg ={colors[x]: f'4{x}' for x in range(8)}


def _colorize(text="", opts=(), **kwargs):
    codes = []
    if text == "" and len(opts) == 1 and opts[0] == "reset":
        return '\x1b[%sm' % RESET
    for k, v in kwargs.items():
        if k == "fg":
            codes.append(fg[v])
        elif k == "bg":
            codes.append(bg[v])
    for o in opts:
        if o in opt_dict:
            codes.append(opt_dict[o])
    if "norest" not in opts:
        text = '%s\x1b[%sm' % (text or '', RESET)
    return '%s%s' % (('\x1b[%sm' % ';'.join(codes)), text or '')


def create_colors(opts=(), **kwargs):
    return lambda text: _colorize(text, opts, **kwargs)


black   = create_colors(fg="black")
red     = create_colors(fg="red")
green   = create_colors(fg="green")
yellow  = create_colors(fg="yellow")
blue    = create_colors(fg="blue")
magenta = create_colors(fg="magenta")
cyan    = create_colors(fg="cyan")
white   = create_colors(fg="white")