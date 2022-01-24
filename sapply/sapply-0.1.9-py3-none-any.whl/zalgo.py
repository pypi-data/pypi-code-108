import random

zalgo_up = [
     # 1         , 2          , 3          , 4
    u'\u030d'    , u'\u030e'  , u'\u0304'  , u'\u0305', # 1     ̍     -2-     ̎    -3-     ̄     -4-     ̅     -=-
    u'\u033f'    , u'\u0311'  , u'\u0306'  , u'\u0310', # 1     ̿     -2-     ̑    -3-     ̆     -4-     ̐     -=-
    u'\u0352'    , u'\u0357'  , u'\u0351'  , u'\u0307', # 1     ͒     -2-     ͗    -3-     ͑     -4-     ̇     -=-
    u'\u0308'    , u'\u030a'  , u'\u0342'  , u'\u0343', # 1     ̈     -2-     ̊    -3-     ͂     -4-     ̓     -=-
    u'\u0344'    , u'\u034a'  , u'\u034b'  , u'\u034c', # 1     ̈́     -2-     ͊    -3-     ͋     -4-     ͌     -=-
    u'\u0303'    , u'\u0302'  , u'\u030c'  , u'\u0350', # 1     ̃     -2-     ̂    -3-     ̌     -4-     ͐     -=-
    u'\u0300'    , u'\u0301'  , u'\u030b'  , u'\u030f', # 1     ̀     -2-     ́    -3-     ̋     -4-     ̏     -=-
    u'\u0312'    , u'\u0313'  , u'\u0314'  , u'\u033d', # 1     ̒     -2-     ̓    -3-     ̔     -4-     ̽     -=-
    u'\u0309'    , u'\u0363'  , u'\u0364'  , u'\u0365', # 1     ̉     -2-     ͣ    -3-     ͤ     -4-     ͥ     -=-
    u'\u0366'    , u'\u0367'  , u'\u0368'  , u'\u0369', # 1     ͦ     -2-     ͧ    -3-     ͨ     -4-     ͩ     -=-
    u'\u036a'    , u'\u036b'  , u'\u036c'  , u'\u036d', # 1     ͪ     -2-     ͫ    -3-     ͬ     -4-     ͭ     -=-
    u'\u036e'    , u'\u036f'  , u'\u033e'  , u'\u035b', # 1     ͮ     -2-     ͯ    -3-     ̾     -4-     ͛     -=-
    u'\u0346'    , u'\u031a'                            # 1     ͆     -2-    ̚     -3-
]

zalgo_down = [
     # 1         , 2          , 3          , 4
     u'\u0316'   , u'\u0317'  , u'\u0318'  , u'\u0319', # 1     ̖     -2-     ̗     -3-     ̘     -4-     ̙    -=-
     u'\u031c'   , u'\u031d'  , u'\u031e'  , u'\u031f', # 1     ̜     -2-     ̝     -3-     ̞     -4-     ̟    -=-
     u'\u0320'   , u'\u0324'  , u'\u0325'  , u'\u0326', # 1     ̠     -2-     ̤     -3-     ̥     -4-     ̦    -=-
     u'\u0329'   , u'\u032a'  , u'\u032b'  , u'\u032c', # 1     ̩     -2-     ̪     -3-     ̫     -4-     ̬    -=-
     u'\u032d'   , u'\u032e'  , u'\u032f'  , u'\u0330', # 1     ̭     -2-     ̮     -3-     ̯     -4-     ̰    -=-
     u'\u0331'   , u'\u0332'  , u'\u0333'  , u'\u0339', # 1     ̱     -2-     ̲     -3-     ̳     -4-     ̹    -=-
     u'\u033a'   , u'\u033b'  , u'\u033c'  , u'\u0345', # 1     ̺     -2-     ̻     -3-     ̼     -4-     ͅ    -=-
     u'\u0347'   , u'\u0348'  , u'\u0349'  , u'\u034d', # 1     ͇     -2-     ͈     -3-     ͉     -4-     ͍    -=-
     u'\u034e'   , u'\u0353'  , u'\u0354'  , u'\u0355', # 1     ͎     -2-     ͓     -3-     ͔     -4-     ͕    -=-
     u'\u0356'   , u'\u0359'  , u'\u035a'  , u'\u0323'  # 1     ͖     -2-     ͙     -3-     ͚     -4-    ̣     -=-
]

zalgo_mid = [
     # 1         , 2          , 3          , 4
     u'\u0315'   , u'\u031b'  , u'\u0340'  , u'\u0341', # 1     ̕     -2-     ̛     -3-     ̀     -4-     ́     -=-
     u'\u0358'   , u'\u0321'  , u'\u0322'  , u'\u0327', # 1     ͘     -2-     ̡     -3-     ̢     -4-     ̧     -=-
     u'\u0328'   , u'\u0334'  , u'\u0335'  , u'\u0336', # 1     ̨     -2-     ̴     -3-     ̵     -4-     ̶     -=-
     u'\u034f'   , u'\u035c'  , u'\u035d'  , u'\u035e', # 1     ͏     -2-     ͜     -3-     ͝     -4-     ͞     -=-
     u'\u035f'   , u'\u0360'  , u'\u0362'  , u'\u0338', # 1     ͟     -2-     ͠     -3-     ͢     -4-     ̸     -=-
     u'\u0337'   , u'\u0361'  , u'\u0489'               # 1     ̷     -2-     ͡     -3-    ҉_     -4-          -=-
]

def rand(*integers):
    return tuple([random.randint(0, i) for i in integers])

def rand_zalgo(array):
    ind = random.randint(0, len(array) - 1)
    return array[ind]

def is_zalgo_char(c):
    char_map = [zalgo_up, zalgo_mid, zalgo_down]
    for cmap in char_map:
        for char in cmap:
            if c == char:
                return True
    return False

def to_zalgo(out, option, char_length, char_list):
    if option:
        for char in range(0, char_length):
            out += rand_zalgo(char_list)
    return out

def normalize(num_tuple, base, exp):
    num_up, num_mid, num_down = num_tuple

    def norm(*numbers):
        result = []
        for num in numbers:
            divisor = base ** exp
            result.append(int((num / divisor) + divisor - 1))
        return tuple(result)
    return norm(num_up, num_mid, num_down)

def zalgo(text, up=False, mid=True, down=True, intensity='mini'):
    out = ''
    for char in text:
        if is_zalgo_char(char):
            continue
        out += char
        if (intensity == 'mini'):
            num_up, num_mid, num_down = rand(8, 2, 8)
        elif (intensity == 'normal'):
            num_up, num_mid, num_down = normalize(rand(16, 6, 16), 2, 1)
        elif (intensity == 'maxi'):
            num_up, num_mid, num_down = normalize(rand(64, 16, 64), 2, 4)
        out = to_zalgo(out, up    , num_up    , zalgo_up)
        out = to_zalgo(out, down  , num_down  , zalgo_down)
        out = to_zalgo(out, mid   , num_mid   , zalgo_mid)

    print(out)
