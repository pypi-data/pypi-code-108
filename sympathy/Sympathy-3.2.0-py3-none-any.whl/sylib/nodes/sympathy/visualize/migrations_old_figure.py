# This file is part of Sympathy for Data.
# Copyright (c) 2020, Combine Control Systems AB
#
# Sympathy for Data is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# Sympathy for Data is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sympathy for Data.  If not, see <http://www.gnu.org/licenses/>.
import re
import json
import copy

import numpy as np

from sympathy.api import node as synode
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags
from sympathy.platform import migrations


# Properties that are only allowed to be python in the new model.
_py_only_props = [
    'xdata',
    'ydata',
    'zdata',
    'xerr',
    'yerr',
    'startx',
    'starty',
    'endx',
    'endy',
    'weights',
    'labels',
    'colors',
    'center',
    'zlabels',
    'bin_labels',
    'bar_labels',
    'positions',
    'bin_min_edges',
    'bin_max_edges',
    'values',
    'last_step',
    'image',
    'origo',
    'minor_ticks',
    'major_ticks',
    'width',
    'height',
]


_text_to_float = [
    'SY_COLORMAP_MIN_PARAMS',
    'SY_COLORMAP_MAX_PARAMS',
    'SY_MARKER_SIZE_PARAMS',
    'SY_ROTATION_PARAMS',
    'explode',
    'annotate_x',
    'annotate_y',
    'shrink',
    'arrow_width',
    'arrow_headwidth',
    'arrow_length',
    'labeldistance',
    'radius',
    'textx',
    'texty',
    'y_start',
    'y_height',
    'capsize',
    'capthick',
    'elinewidth',
]


_text_to_bool = [
        'SY_FILLED_PARAMS',
        'show',
        'frameon',
        'labelhide',
        # (shadow)
        'notch',
        'text_visible',
        'add_to_legend',
        'visible',
]


mpl_colornames = {
    "xkcd:cloudy blue": "#acc2d9",
    "xkcd:dark pastel green": "#56ae57",
    "xkcd:dust": "#b2996e",
    "xkcd:electric lime": "#a8ff04",
    "xkcd:fresh green": "#69d84f",
    "xkcd:light eggplant": "#894585",
    "xkcd:nasty green": "#70b23f",
    "xkcd:really light blue": "#d4ffff",
    "xkcd:tea": "#65ab7c",
    "xkcd:warm purple": "#952e8f",
    "xkcd:yellowish tan": "#fcfc81",
    "xkcd:cement": "#a5a391",
    "xkcd:dark grass green": "#388004",
    "xkcd:dusty teal": "#4c9085",
    "xkcd:grey teal": "#5e9b8a",
    "xkcd:macaroni and cheese": "#efb435",
    "xkcd:pinkish tan": "#d99b82",
    "xkcd:spruce": "#0a5f38",
    "xkcd:strong blue": "#0c06f7",
    "xkcd:toxic green": "#61de2a",
    "xkcd:windows blue": "#3778bf",
    "xkcd:blue blue": "#2242c7",
    "xkcd:blue with a hint of purple": "#533cc6",
    "xkcd:booger": "#9bb53c",
    "xkcd:bright sea green": "#05ffa6",
    "xkcd:dark green blue": "#1f6357",
    "xkcd:deep turquoise": "#017374",
    "xkcd:green teal": "#0cb577",
    "xkcd:strong pink": "#ff0789",
    "xkcd:bland": "#afa88b",
    "xkcd:deep aqua": "#08787f",
    "xkcd:lavender pink": "#dd85d7",
    "xkcd:light moss green": "#a6c875",
    "xkcd:light seafoam green": "#a7ffb5",
    "xkcd:olive yellow": "#c2b709",
    "xkcd:pig pink": "#e78ea5",
    "xkcd:deep lilac": "#966ebd",
    "xkcd:desert": "#ccad60",
    "xkcd:dusty lavender": "#ac86a8",
    "xkcd:purpley grey": "#947e94",
    "xkcd:purply": "#983fb2",
    "xkcd:candy pink": "#ff63e9",
    "xkcd:light pastel green": "#b2fba5",
    "xkcd:boring green": "#63b365",
    "xkcd:kiwi green": "#8ee53f",
    "xkcd:light grey green": "#b7e1a1",
    "xkcd:orange pink": "#ff6f52",
    "xkcd:tea green": "#bdf8a3",
    "xkcd:very light brown": "#d3b683",
    "xkcd:egg shell": "#fffcc4",
    "xkcd:eggplant purple": "#430541",
    "xkcd:powder pink": "#ffb2d0",
    "xkcd:reddish grey": "#997570",
    "xkcd:baby shit brown": "#ad900d",
    "xkcd:liliac": "#c48efd",
    "xkcd:stormy blue": "#507b9c",
    "xkcd:ugly brown": "#7d7103",
    "xkcd:custard": "#fffd78",
    "xkcd:darkish pink": "#da467d",
    "xkcd:deep brown": "#410200",
    "xkcd:greenish beige": "#c9d179",
    "xkcd:manilla": "#fffa86",
    "xkcd:off blue": "#5684ae",
    "xkcd:battleship grey": "#6b7c85",
    "xkcd:browny green": "#6f6c0a",
    "xkcd:bruise": "#7e4071",
    "xkcd:kelley green": "#009337",
    "xkcd:sickly yellow": "#d0e429",
    "xkcd:sunny yellow": "#fff917",
    "xkcd:azul": "#1d5dec",
    "xkcd:darkgreen": "#054907",
    "xkcd:green/yellow": "#b5ce08",
    "xkcd:lichen": "#8fb67b",
    "xkcd:light light green": "#c8ffb0",
    "xkcd:pale gold": "#fdde6c",
    "xkcd:sun yellow": "#ffdf22",
    "xkcd:tan green": "#a9be70",
    "xkcd:burple": "#6832e3",
    "xkcd:butterscotch": "#fdb147",
    "xkcd:toupe": "#c7ac7d",
    "xkcd:dark cream": "#fff39a",
    "xkcd:indian red": "#850e04",
    "xkcd:light lavendar": "#efc0fe",
    "xkcd:poison green": "#40fd14",
    "xkcd:baby puke green": "#b6c406",
    "xkcd:bright yellow green": "#9dff00",
    "xkcd:charcoal grey": "#3c4142",
    "xkcd:squash": "#f2ab15",
    "xkcd:cinnamon": "#ac4f06",
    "xkcd:light pea green": "#c4fe82",
    "xkcd:radioactive green": "#2cfa1f",
    "xkcd:raw sienna": "#9a6200",
    "xkcd:baby purple": "#ca9bf7",
    "xkcd:cocoa": "#875f42",
    "xkcd:light royal blue": "#3a2efe",
    "xkcd:orangeish": "#fd8d49",
    "xkcd:rust brown": "#8b3103",
    "xkcd:sand brown": "#cba560",
    "xkcd:swamp": "#698339",
    "xkcd:tealish green": "#0cdc73",
    "xkcd:burnt siena": "#b75203",
    "xkcd:camo": "#7f8f4e",
    "xkcd:dusk blue": "#26538d",
    "xkcd:fern": "#63a950",
    "xkcd:old rose": "#c87f89",
    "xkcd:pale light green": "#b1fc99",
    "xkcd:peachy pink": "#ff9a8a",
    "xkcd:rosy pink": "#f6688e",
    "xkcd:light bluish green": "#76fda8",
    "xkcd:light bright green": "#53fe5c",
    "xkcd:light neon green": "#4efd54",
    "xkcd:light seafoam": "#a0febf",
    "xkcd:tiffany blue": "#7bf2da",
    "xkcd:washed out green": "#bcf5a6",
    "xkcd:browny orange": "#ca6b02",
    "xkcd:nice blue": "#107ab0",
    "xkcd:sapphire": "#2138ab",
    "xkcd:greyish teal": "#719f91",
    "xkcd:orangey yellow": "#fdb915",
    "xkcd:parchment": "#fefcaf",
    "xkcd:straw": "#fcf679",
    "xkcd:very dark brown": "#1d0200",
    "xkcd:terracota": "#cb6843",
    "xkcd:ugly blue": "#31668a",
    "xkcd:clear blue": "#247afd",
    "xkcd:creme": "#ffffb6",
    "xkcd:foam green": "#90fda9",
    "xkcd:grey/green": "#86a17d",
    "xkcd:light gold": "#fddc5c",
    "xkcd:seafoam blue": "#78d1b6",
    "xkcd:topaz": "#13bbaf",
    "xkcd:violet pink": "#fb5ffc",
    "xkcd:wintergreen": "#20f986",
    "xkcd:yellow tan": "#ffe36e",
    "xkcd:dark fuchsia": "#9d0759",
    "xkcd:indigo blue": "#3a18b1",
    "xkcd:light yellowish green": "#c2ff89",
    "xkcd:pale magenta": "#d767ad",
    "xkcd:rich purple": "#720058",
    "xkcd:sunflower yellow": "#ffda03",
    "xkcd:green/blue": "#01c08d",
    "xkcd:leather": "#ac7434",
    "xkcd:racing green": "#014600",
    "xkcd:vivid purple": "#9900fa",
    "xkcd:dark royal blue": "#02066f",
    "xkcd:hazel": "#8e7618",
    "xkcd:muted pink": "#d1768f",
    "xkcd:booger green": "#96b403",
    "xkcd:canary": "#fdff63",
    "xkcd:cool grey": "#95a3a6",
    "xkcd:dark taupe": "#7f684e",
    "xkcd:darkish purple": "#751973",
    "xkcd:true green": "#089404",
    "xkcd:coral pink": "#ff6163",
    "xkcd:dark sage": "#598556",
    "xkcd:dark slate blue": "#214761",
    "xkcd:flat blue": "#3c73a8",
    "xkcd:mushroom": "#ba9e88",
    "xkcd:rich blue": "#021bf9",
    "xkcd:dirty purple": "#734a65",
    "xkcd:greenblue": "#23c48b",
    "xkcd:icky green": "#8fae22",
    "xkcd:light khaki": "#e6f2a2",
    "xkcd:warm blue": "#4b57db",
    "xkcd:dark hot pink": "#d90166",
    "xkcd:deep sea blue": "#015482",
    "xkcd:carmine": "#9d0216",
    "xkcd:dark yellow green": "#728f02",
    "xkcd:pale peach": "#ffe5ad",
    "xkcd:plum purple": "#4e0550",
    "xkcd:golden rod": "#f9bc08",
    "xkcd:neon red": "#ff073a",
    "xkcd:old pink": "#c77986",
    "xkcd:very pale blue": "#d6fffe",
    "xkcd:blood orange": "#fe4b03",
    "xkcd:grapefruit": "#fd5956",
    "xkcd:sand yellow": "#fce166",
    "xkcd:clay brown": "#b2713d",
    "xkcd:dark blue grey": "#1f3b4d",
    "xkcd:flat green": "#699d4c",
    "xkcd:light green blue": "#56fca2",
    "xkcd:warm pink": "#fb5581",
    "xkcd:dodger blue": "#3e82fc",
    "xkcd:gross green": "#a0bf16",
    "xkcd:ice": "#d6fffa",
    "xkcd:metallic blue": "#4f738e",
    "xkcd:pale salmon": "#ffb19a",
    "xkcd:sap green": "#5c8b15",
    "xkcd:algae": "#54ac68",
    "xkcd:bluey grey": "#89a0b0",
    "xkcd:greeny grey": "#7ea07a",
    "xkcd:highlighter green": "#1bfc06",
    "xkcd:light light blue": "#cafffb",
    "xkcd:light mint": "#b6ffbb",
    "xkcd:raw umber": "#a75e09",
    "xkcd:vivid blue": "#152eff",
    "xkcd:deep lavender": "#8d5eb7",
    "xkcd:dull teal": "#5f9e8f",
    "xkcd:light greenish blue": "#63f7b4",
    "xkcd:mud green": "#606602",
    "xkcd:pinky": "#fc86aa",
    "xkcd:red wine": "#8c0034",
    "xkcd:shit green": "#758000",
    "xkcd:tan brown": "#ab7e4c",
    "xkcd:darkblue": "#030764",
    "xkcd:rosa": "#fe86a4",
    "xkcd:lipstick": "#d5174e",
    "xkcd:pale mauve": "#fed0fc",
    "xkcd:claret": "#680018",
    "xkcd:dandelion": "#fedf08",
    "xkcd:orangered": "#fe420f",
    "xkcd:poop green": "#6f7c00",
    "xkcd:ruby": "#ca0147",
    "xkcd:dark": "#1b2431",
    "xkcd:greenish turquoise": "#00fbb0",
    "xkcd:pastel red": "#db5856",
    "xkcd:piss yellow": "#ddd618",
    "xkcd:bright cyan": "#41fdfe",
    "xkcd:dark coral": "#cf524e",
    "xkcd:algae green": "#21c36f",
    "xkcd:darkish red": "#a90308",
    "xkcd:reddy brown": "#6e1005",
    "xkcd:blush pink": "#fe828c",
    "xkcd:camouflage green": "#4b6113",
    "xkcd:lawn green": "#4da409",
    "xkcd:putty": "#beae8a",
    "xkcd:vibrant blue": "#0339f8",
    "xkcd:dark sand": "#a88f59",
    "xkcd:purple/blue": "#5d21d0",
    "xkcd:saffron": "#feb209",
    "xkcd:twilight": "#4e518b",
    "xkcd:warm brown": "#964e02",
    "xkcd:bluegrey": "#85a3b2",
    "xkcd:bubble gum pink": "#ff69af",
    "xkcd:duck egg blue": "#c3fbf4",
    "xkcd:greenish cyan": "#2afeb7",
    "xkcd:petrol": "#005f6a",
    "xkcd:royal": "#0c1793",
    "xkcd:butter": "#ffff81",
    "xkcd:dusty orange": "#f0833a",
    "xkcd:off yellow": "#f1f33f",
    "xkcd:pale olive green": "#b1d27b",
    "xkcd:orangish": "#fc824a",
    "xkcd:leaf": "#71aa34",
    "xkcd:light blue grey": "#b7c9e2",
    "xkcd:dried blood": "#4b0101",
    "xkcd:lightish purple": "#a552e6",
    "xkcd:rusty red": "#af2f0d",
    "xkcd:lavender blue": "#8b88f8",
    "xkcd:light grass green": "#9af764",
    "xkcd:light mint green": "#a6fbb2",
    "xkcd:sunflower": "#ffc512",
    "xkcd:velvet": "#750851",
    "xkcd:brick orange": "#c14a09",
    "xkcd:lightish red": "#fe2f4a",
    "xkcd:pure blue": "#0203e2",
    "xkcd:twilight blue": "#0a437a",
    "xkcd:violet red": "#a50055",
    "xkcd:yellowy brown": "#ae8b0c",
    "xkcd:carnation": "#fd798f",
    "xkcd:muddy yellow": "#bfac05",
    "xkcd:dark seafoam green": "#3eaf76",
    "xkcd:deep rose": "#c74767",
    "xkcd:dusty red": "#b9484e",
    "xkcd:grey/blue": "#647d8e",
    "xkcd:lemon lime": "#bffe28",
    "xkcd:purple/pink": "#d725de",
    "xkcd:brown yellow": "#b29705",
    "xkcd:purple brown": "#673a3f",
    "xkcd:wisteria": "#a87dc2",
    "xkcd:banana yellow": "#fafe4b",
    "xkcd:lipstick red": "#c0022f",
    "xkcd:water blue": "#0e87cc",
    "xkcd:brown grey": "#8d8468",
    "xkcd:vibrant purple": "#ad03de",
    "xkcd:baby green": "#8cff9e",
    "xkcd:barf green": "#94ac02",
    "xkcd:eggshell blue": "#c4fff7",
    "xkcd:sandy yellow": "#fdee73",
    "xkcd:cool green": "#33b864",
    "xkcd:pale": "#fff9d0",
    "xkcd:blue/grey": "#758da3",
    "xkcd:hot magenta": "#f504c9",
    "xkcd:greyblue": "#77a1b5",
    "xkcd:purpley": "#8756e4",
    "xkcd:baby shit green": "#889717",
    "xkcd:brownish pink": "#c27e79",
    "xkcd:dark aquamarine": "#017371",
    "xkcd:diarrhea": "#9f8303",
    "xkcd:light mustard": "#f7d560",
    "xkcd:pale sky blue": "#bdf6fe",
    "xkcd:turtle green": "#75b84f",
    "xkcd:bright olive": "#9cbb04",
    "xkcd:dark grey blue": "#29465b",
    "xkcd:greeny brown": "#696006",
    "xkcd:lemon green": "#adf802",
    "xkcd:light periwinkle": "#c1c6fc",
    "xkcd:seaweed green": "#35ad6b",
    "xkcd:sunshine yellow": "#fffd37",
    "xkcd:ugly purple": "#a442a0",
    "xkcd:medium pink": "#f36196",
    "xkcd:puke brown": "#947706",
    "xkcd:very light pink": "#fff4f2",
    "xkcd:viridian": "#1e9167",
    "xkcd:bile": "#b5c306",
    "xkcd:faded yellow": "#feff7f",
    "xkcd:very pale green": "#cffdbc",
    "xkcd:vibrant green": "#0add08",
    "xkcd:bright lime": "#87fd05",
    "xkcd:spearmint": "#1ef876",
    "xkcd:light aquamarine": "#7bfdc7",
    "xkcd:light sage": "#bcecac",
    "xkcd:yellowgreen": "#bbf90f",
    "xkcd:baby poo": "#ab9004",
    "xkcd:dark seafoam": "#1fb57a",
    "xkcd:deep teal": "#00555a",
    "xkcd:heather": "#a484ac",
    "xkcd:rust orange": "#c45508",
    "xkcd:dirty blue": "#3f829d",
    "xkcd:fern green": "#548d44",
    "xkcd:bright lilac": "#c95efb",
    "xkcd:weird green": "#3ae57f",
    "xkcd:peacock blue": "#016795",
    "xkcd:avocado green": "#87a922",
    "xkcd:faded orange": "#f0944d",
    "xkcd:grape purple": "#5d1451",
    "xkcd:hot green": "#25ff29",
    "xkcd:lime yellow": "#d0fe1d",
    "xkcd:mango": "#ffa62b",
    "xkcd:shamrock": "#01b44c",
    "xkcd:bubblegum": "#ff6cb5",
    "xkcd:purplish brown": "#6b4247",
    "xkcd:vomit yellow": "#c7c10c",
    "xkcd:pale cyan": "#b7fffa",
    "xkcd:key lime": "#aeff6e",
    "xkcd:tomato red": "#ec2d01",
    "xkcd:lightgreen": "#76ff7b",
    "xkcd:merlot": "#730039",
    "xkcd:night blue": "#040348",
    "xkcd:purpleish pink": "#df4ec8",
    "xkcd:apple": "#6ecb3c",
    "xkcd:baby poop green": "#8f9805",
    "xkcd:green apple": "#5edc1f",
    "xkcd:heliotrope": "#d94ff5",
    "xkcd:yellow/green": "#c8fd3d",
    "xkcd:almost black": "#070d0d",
    "xkcd:cool blue": "#4984b8",
    "xkcd:leafy green": "#51b73b",
    "xkcd:mustard brown": "#ac7e04",
    "xkcd:dusk": "#4e5481",
    "xkcd:dull brown": "#876e4b",
    "xkcd:frog green": "#58bc08",
    "xkcd:vivid green": "#2fef10",
    "xkcd:bright light green": "#2dfe54",
    "xkcd:fluro green": "#0aff02",
    "xkcd:kiwi": "#9cef43",
    "xkcd:seaweed": "#18d17b",
    "xkcd:navy green": "#35530a",
    "xkcd:ultramarine blue": "#1805db",
    "xkcd:iris": "#6258c4",
    "xkcd:pastel orange": "#ff964f",
    "xkcd:yellowish orange": "#ffab0f",
    "xkcd:perrywinkle": "#8f8ce7",
    "xkcd:tealish": "#24bca8",
    "xkcd:dark plum": "#3f012c",
    "xkcd:pear": "#cbf85f",
    "xkcd:pinkish orange": "#ff724c",
    "xkcd:midnight purple": "#280137",
    "xkcd:light urple": "#b36ff6",
    "xkcd:dark mint": "#48c072",
    "xkcd:greenish tan": "#bccb7a",
    "xkcd:light burgundy": "#a8415b",
    "xkcd:turquoise blue": "#06b1c4",
    "xkcd:ugly pink": "#cd7584",
    "xkcd:sandy": "#f1da7a",
    "xkcd:electric pink": "#ff0490",
    "xkcd:muted purple": "#805b87",
    "xkcd:mid green": "#50a747",
    "xkcd:greyish": "#a8a495",
    "xkcd:neon yellow": "#cfff04",
    "xkcd:banana": "#ffff7e",
    "xkcd:carnation pink": "#ff7fa7",
    "xkcd:tomato": "#ef4026",
    "xkcd:sea": "#3c9992",
    "xkcd:muddy brown": "#886806",
    "xkcd:turquoise green": "#04f489",
    "xkcd:buff": "#fef69e",
    "xkcd:fawn": "#cfaf7b",
    "xkcd:muted blue": "#3b719f",
    "xkcd:pale rose": "#fdc1c5",
    "xkcd:dark mint green": "#20c073",
    "xkcd:amethyst": "#9b5fc0",
    "xkcd:blue/green": "#0f9b8e",
    "xkcd:chestnut": "#742802",
    "xkcd:sick green": "#9db92c",
    "xkcd:pea": "#a4bf20",
    "xkcd:rusty orange": "#cd5909",
    "xkcd:stone": "#ada587",
    "xkcd:rose red": "#be013c",
    "xkcd:pale aqua": "#b8ffeb",
    "xkcd:deep orange": "#dc4d01",
    "xkcd:earth": "#a2653e",
    "xkcd:mossy green": "#638b27",
    "xkcd:grassy green": "#419c03",
    "xkcd:pale lime green": "#b1ff65",
    "xkcd:light grey blue": "#9dbcd4",
    "xkcd:pale grey": "#fdfdfe",
    "xkcd:asparagus": "#77ab56",
    "xkcd:blueberry": "#464196",
    "xkcd:purple red": "#990147",
    "xkcd:pale lime": "#befd73",
    "xkcd:greenish teal": "#32bf84",
    "xkcd:caramel": "#af6f09",
    "xkcd:deep magenta": "#a0025c",
    "xkcd:light peach": "#ffd8b1",
    "xkcd:milk chocolate": "#7f4e1e",
    "xkcd:ocher": "#bf9b0c",
    "xkcd:off green": "#6ba353",
    "xkcd:purply pink": "#f075e6",
    "xkcd:lightblue": "#7bc8f6",
    "xkcd:dusky blue": "#475f94",
    "xkcd:golden": "#f5bf03",
    "xkcd:light beige": "#fffeb6",
    "xkcd:butter yellow": "#fffd74",
    "xkcd:dusky purple": "#895b7b",
    "xkcd:french blue": "#436bad",
    "xkcd:ugly yellow": "#d0c101",
    "xkcd:greeny yellow": "#c6f808",
    "xkcd:orangish red": "#f43605",
    "xkcd:shamrock green": "#02c14d",
    "xkcd:orangish brown": "#b25f03",
    "xkcd:tree green": "#2a7e19",
    "xkcd:deep violet": "#490648",
    "xkcd:gunmetal": "#536267",
    "xkcd:blue/purple": "#5a06ef",
    "xkcd:cherry": "#cf0234",
    "xkcd:sandy brown": "#c4a661",
    "xkcd:warm grey": "#978a84",
    "xkcd:dark indigo": "#1f0954",
    "xkcd:midnight": "#03012d",
    "xkcd:bluey green": "#2bb179",
    "xkcd:grey pink": "#c3909b",
    "xkcd:soft purple": "#a66fb5",
    "xkcd:blood": "#770001",
    "xkcd:brown red": "#922b05",
    "xkcd:medium grey": "#7d7f7c",
    "xkcd:berry": "#990f4b",
    "xkcd:poo": "#8f7303",
    "xkcd:purpley pink": "#c83cb9",
    "xkcd:light salmon": "#fea993",
    "xkcd:snot": "#acbb0d",
    "xkcd:easter purple": "#c071fe",
    "xkcd:light yellow green": "#ccfd7f",
    "xkcd:dark navy blue": "#00022e",
    "xkcd:drab": "#828344",
    "xkcd:light rose": "#ffc5cb",
    "xkcd:rouge": "#ab1239",
    "xkcd:purplish red": "#b0054b",
    "xkcd:slime green": "#99cc04",
    "xkcd:baby poop": "#937c00",
    "xkcd:irish green": "#019529",
    "xkcd:pink/purple": "#ef1de7",
    "xkcd:dark navy": "#000435",
    "xkcd:greeny blue": "#42b395",
    "xkcd:light plum": "#9d5783",
    "xkcd:pinkish grey": "#c8aca9",
    "xkcd:dirty orange": "#c87606",
    "xkcd:rust red": "#aa2704",
    "xkcd:pale lilac": "#e4cbff",
    "xkcd:orangey red": "#fa4224",
    "xkcd:primary blue": "#0804f9",
    "xkcd:kermit green": "#5cb200",
    "xkcd:brownish purple": "#76424e",
    "xkcd:murky green": "#6c7a0e",
    "xkcd:wheat": "#fbdd7e",
    "xkcd:very dark purple": "#2a0134",
    "xkcd:bottle green": "#044a05",
    "xkcd:watermelon": "#fd4659",
    "xkcd:deep sky blue": "#0d75f8",
    "xkcd:fire engine red": "#fe0002",
    "xkcd:yellow ochre": "#cb9d06",
    "xkcd:pumpkin orange": "#fb7d07",
    "xkcd:pale olive": "#b9cc81",
    "xkcd:light lilac": "#edc8ff",
    "xkcd:lightish green": "#61e160",
    "xkcd:carolina blue": "#8ab8fe",
    "xkcd:mulberry": "#920a4e",
    "xkcd:shocking pink": "#fe02a2",
    "xkcd:auburn": "#9a3001",
    "xkcd:bright lime green": "#65fe08",
    "xkcd:celadon": "#befdb7",
    "xkcd:pinkish brown": "#b17261",
    "xkcd:poo brown": "#885f01",
    "xkcd:bright sky blue": "#02ccfe",
    "xkcd:celery": "#c1fd95",
    "xkcd:dirt brown": "#836539",
    "xkcd:strawberry": "#fb2943",
    "xkcd:dark lime": "#84b701",
    "xkcd:copper": "#b66325",
    "xkcd:medium brown": "#7f5112",
    "xkcd:muted green": "#5fa052",
    "xkcd:robin's egg": "#6dedfd",
    "xkcd:bright aqua": "#0bf9ea",
    "xkcd:bright lavender": "#c760ff",
    "xkcd:ivory": "#ffffcb",
    "xkcd:very light purple": "#f6cefc",
    "xkcd:light navy": "#155084",
    "xkcd:pink red": "#f5054f",
    "xkcd:olive brown": "#645403",
    "xkcd:poop brown": "#7a5901",
    "xkcd:mustard green": "#a8b504",
    "xkcd:ocean green": "#3d9973",
    "xkcd:very dark blue": "#000133",
    "xkcd:dusty green": "#76a973",
    "xkcd:light navy blue": "#2e5a88",
    "xkcd:minty green": "#0bf77d",
    "xkcd:adobe": "#bd6c48",
    "xkcd:barney": "#ac1db8",
    "xkcd:jade green": "#2baf6a",
    "xkcd:bright light blue": "#26f7fd",
    "xkcd:light lime": "#aefd6c",
    "xkcd:dark khaki": "#9b8f55",
    "xkcd:orange yellow": "#ffad01",
    "xkcd:ocre": "#c69c04",
    "xkcd:maize": "#f4d054",
    "xkcd:faded pink": "#de9dac",
    "xkcd:british racing green": "#05480d",
    "xkcd:sandstone": "#c9ae74",
    "xkcd:mud brown": "#60460f",
    "xkcd:light sea green": "#98f6b0",
    "xkcd:robin egg blue": "#8af1fe",
    "xkcd:aqua marine": "#2ee8bb",
    "xkcd:dark sea green": "#11875d",
    "xkcd:soft pink": "#fdb0c0",
    "xkcd:orangey brown": "#b16002",
    "xkcd:cherry red": "#f7022a",
    "xkcd:burnt yellow": "#d5ab09",
    "xkcd:brownish grey": "#86775f",
    "xkcd:camel": "#c69f59",
    "xkcd:purplish grey": "#7a687f",
    "xkcd:marine": "#042e60",
    "xkcd:greyish pink": "#c88d94",
    "xkcd:pale turquoise": "#a5fbd5",
    "xkcd:pastel yellow": "#fffe71",
    "xkcd:bluey purple": "#6241c7",
    "xkcd:canary yellow": "#fffe40",
    "xkcd:faded red": "#d3494e",
    "xkcd:sepia": "#985e2b",
    "xkcd:coffee": "#a6814c",
    "xkcd:bright magenta": "#ff08e8",
    "xkcd:mocha": "#9d7651",
    "xkcd:ecru": "#feffca",
    "xkcd:purpleish": "#98568d",
    "xkcd:cranberry": "#9e003a",
    "xkcd:darkish green": "#287c37",
    "xkcd:brown orange": "#b96902",
    "xkcd:dusky rose": "#ba6873",
    "xkcd:melon": "#ff7855",
    "xkcd:sickly green": "#94b21c",
    "xkcd:silver": "#c5c9c7",
    "xkcd:purply blue": "#661aee",
    "xkcd:purpleish blue": "#6140ef",
    "xkcd:hospital green": "#9be5aa",
    "xkcd:shit brown": "#7b5804",
    "xkcd:mid blue": "#276ab3",
    "xkcd:amber": "#feb308",
    "xkcd:easter green": "#8cfd7e",
    "xkcd:soft blue": "#6488ea",
    "xkcd:cerulean blue": "#056eee",
    "xkcd:golden brown": "#b27a01",
    "xkcd:bright turquoise": "#0ffef9",
    "xkcd:red pink": "#fa2a55",
    "xkcd:red purple": "#820747",
    "xkcd:greyish brown": "#7a6a4f",
    "xkcd:vermillion": "#f4320c",
    "xkcd:russet": "#a13905",
    "xkcd:steel grey": "#6f828a",
    "xkcd:lighter purple": "#a55af4",
    "xkcd:bright violet": "#ad0afd",
    "xkcd:prussian blue": "#004577",
    "xkcd:slate green": "#658d6d",
    "xkcd:dirty pink": "#ca7b80",
    "xkcd:dark blue green": "#005249",
    "xkcd:pine": "#2b5d34",
    "xkcd:yellowy green": "#bff128",
    "xkcd:dark gold": "#b59410",
    "xkcd:bluish": "#2976bb",
    "xkcd:darkish blue": "#014182",
    "xkcd:dull red": "#bb3f3f",
    "xkcd:pinky red": "#fc2647",
    "xkcd:bronze": "#a87900",
    "xkcd:pale teal": "#82cbb2",
    "xkcd:military green": "#667c3e",
    "xkcd:barbie pink": "#fe46a5",
    "xkcd:bubblegum pink": "#fe83cc",
    "xkcd:pea soup green": "#94a617",
    "xkcd:dark mustard": "#a88905",
    "xkcd:shit": "#7f5f00",
    "xkcd:medium purple": "#9e43a2",
    "xkcd:very dark green": "#062e03",
    "xkcd:dirt": "#8a6e45",
    "xkcd:dusky pink": "#cc7a8b",
    "xkcd:red violet": "#9e0168",
    "xkcd:lemon yellow": "#fdff38",
    "xkcd:pistachio": "#c0fa8b",
    "xkcd:dull yellow": "#eedc5b",
    "xkcd:dark lime green": "#7ebd01",
    "xkcd:denim blue": "#3b5b92",
    "xkcd:teal blue": "#01889f",
    "xkcd:lightish blue": "#3d7afd",
    "xkcd:purpley blue": "#5f34e7",
    "xkcd:light indigo": "#6d5acf",
    "xkcd:swamp green": "#748500",
    "xkcd:brown green": "#706c11",
    "xkcd:dark maroon": "#3c0008",
    "xkcd:hot purple": "#cb00f5",
    "xkcd:dark forest green": "#002d04",
    "xkcd:faded blue": "#658cbb",
    "xkcd:drab green": "#749551",
    "xkcd:light lime green": "#b9ff66",
    "xkcd:snot green": "#9dc100",
    "xkcd:yellowish": "#faee66",
    "xkcd:light blue green": "#7efbb3",
    "xkcd:bordeaux": "#7b002c",
    "xkcd:light mauve": "#c292a1",
    "xkcd:ocean": "#017b92",
    "xkcd:marigold": "#fcc006",
    "xkcd:muddy green": "#657432",
    "xkcd:dull orange": "#d8863b",
    "xkcd:steel": "#738595",
    "xkcd:electric purple": "#aa23ff",
    "xkcd:fluorescent green": "#08ff08",
    "xkcd:yellowish brown": "#9b7a01",
    "xkcd:blush": "#f29e8e",
    "xkcd:soft green": "#6fc276",
    "xkcd:bright orange": "#ff5b00",
    "xkcd:lemon": "#fdff52",
    "xkcd:purple grey": "#866f85",
    "xkcd:acid green": "#8ffe09",
    "xkcd:pale lavender": "#eecffe",
    "xkcd:violet blue": "#510ac9",
    "xkcd:light forest green": "#4f9153",
    "xkcd:burnt red": "#9f2305",
    "xkcd:khaki green": "#728639",
    "xkcd:cerise": "#de0c62",
    "xkcd:faded purple": "#916e99",
    "xkcd:apricot": "#ffb16d",
    "xkcd:dark olive green": "#3c4d03",
    "xkcd:grey brown": "#7f7053",
    "xkcd:green grey": "#77926f",
    "xkcd:true blue": "#010fcc",
    "xkcd:pale violet": "#ceaefa",
    "xkcd:periwinkle blue": "#8f99fb",
    "xkcd:light sky blue": "#c6fcff",
    "xkcd:blurple": "#5539cc",
    "xkcd:green brown": "#544e03",
    "xkcd:bluegreen": "#017a79",
    "xkcd:bright teal": "#01f9c6",
    "xkcd:brownish yellow": "#c9b003",
    "xkcd:pea soup": "#929901",
    "xkcd:forest": "#0b5509",
    "xkcd:barney purple": "#a00498",
    "xkcd:ultramarine": "#2000b1",
    "xkcd:purplish": "#94568c",
    "xkcd:puke yellow": "#c2be0e",
    "xkcd:bluish grey": "#748b97",
    "xkcd:dark periwinkle": "#665fd1",
    "xkcd:dark lilac": "#9c6da5",
    "xkcd:reddish": "#c44240",
    "xkcd:light maroon": "#a24857",
    "xkcd:dusty purple": "#825f87",
    "xkcd:terra cotta": "#c9643b",
    "xkcd:avocado": "#90b134",
    "xkcd:marine blue": "#01386a",
    "xkcd:teal green": "#25a36f",
    "xkcd:slate grey": "#59656d",
    "xkcd:lighter green": "#75fd63",
    "xkcd:electric green": "#21fc0d",
    "xkcd:dusty blue": "#5a86ad",
    "xkcd:golden yellow": "#fec615",
    "xkcd:bright yellow": "#fffd01",
    "xkcd:light lavender": "#dfc5fe",
    "xkcd:umber": "#b26400",
    "xkcd:poop": "#7f5e00",
    "xkcd:dark peach": "#de7e5d",
    "xkcd:jungle green": "#048243",
    "xkcd:eggshell": "#ffffd4",
    "xkcd:denim": "#3b638c",
    "xkcd:yellow brown": "#b79400",
    "xkcd:dull purple": "#84597e",
    "xkcd:chocolate brown": "#411900",
    "xkcd:wine red": "#7b0323",
    "xkcd:neon blue": "#04d9ff",
    "xkcd:dirty green": "#667e2c",
    "xkcd:light tan": "#fbeeac",
    "xkcd:ice blue": "#d7fffe",
    "xkcd:cadet blue": "#4e7496",
    "xkcd:dark mauve": "#874c62",
    "xkcd:very light blue": "#d5ffff",
    "xkcd:grey purple": "#826d8c",
    "xkcd:pastel pink": "#ffbacd",
    "xkcd:very light green": "#d1ffbd",
    "xkcd:dark sky blue": "#448ee4",
    "xkcd:evergreen": "#05472a",
    "xkcd:dull pink": "#d5869d",
    "xkcd:aubergine": "#3d0734",
    "xkcd:mahogany": "#4a0100",
    "xkcd:reddish orange": "#f8481c",
    "xkcd:deep green": "#02590f",
    "xkcd:vomit green": "#89a203",
    "xkcd:purple pink": "#e03fd8",
    "xkcd:dusty pink": "#d58a94",
    "xkcd:faded green": "#7bb274",
    "xkcd:camo green": "#526525",
    "xkcd:pinky purple": "#c94cbe",
    "xkcd:pink purple": "#db4bda",
    "xkcd:brownish red": "#9e3623",
    "xkcd:dark rose": "#b5485d",
    "xkcd:mud": "#735c12",
    "xkcd:brownish": "#9c6d57",
    "xkcd:emerald green": "#028f1e",
    "xkcd:pale brown": "#b1916e",
    "xkcd:dull blue": "#49759c",
    "xkcd:burnt umber": "#a0450e",
    "xkcd:medium green": "#39ad48",
    "xkcd:clay": "#b66a50",
    "xkcd:light aqua": "#8cffdb",
    "xkcd:light olive green": "#a4be5c",
    "xkcd:brownish orange": "#cb7723",
    "xkcd:dark aqua": "#05696b",
    "xkcd:purplish pink": "#ce5dae",
    "xkcd:dark salmon": "#c85a53",
    "xkcd:greenish grey": "#96ae8d",
    "xkcd:jade": "#1fa774",
    "xkcd:ugly green": "#7a9703",
    "xkcd:dark beige": "#ac9362",
    "xkcd:emerald": "#01a049",
    "xkcd:pale red": "#d9544d",
    "xkcd:light magenta": "#fa5ff7",
    "xkcd:sky": "#82cafc",
    "xkcd:light cyan": "#acfffc",
    "xkcd:yellow orange": "#fcb001",
    "xkcd:reddish purple": "#910951",
    "xkcd:reddish pink": "#fe2c54",
    "xkcd:orchid": "#c875c4",
    "xkcd:dirty yellow": "#cdc50a",
    "xkcd:orange red": "#fd411e",
    "xkcd:deep red": "#9a0200",
    "xkcd:orange brown": "#be6400",
    "xkcd:cobalt blue": "#030aa7",
    "xkcd:neon pink": "#fe019a",
    "xkcd:rose pink": "#f7879a",
    "xkcd:greyish purple": "#887191",
    "xkcd:raspberry": "#b00149",
    "xkcd:aqua green": "#12e193",
    "xkcd:salmon pink": "#fe7b7c",
    "xkcd:tangerine": "#ff9408",
    "xkcd:brownish green": "#6a6e09",
    "xkcd:red brown": "#8b2e16",
    "xkcd:greenish brown": "#696112",
    "xkcd:pumpkin": "#e17701",
    "xkcd:pine green": "#0a481e",
    "xkcd:charcoal": "#343837",
    "xkcd:baby pink": "#ffb7ce",
    "xkcd:cornflower": "#6a79f7",
    "xkcd:blue violet": "#5d06e9",
    "xkcd:chocolate": "#3d1c02",
    "xkcd:greyish green": "#82a67d",
    "xkcd:scarlet": "#be0119",
    "xkcd:green yellow": "#c9ff27",
    "xkcd:dark olive": "#373e02",
    "xkcd:sienna": "#a9561e",
    "xkcd:pastel purple": "#caa0ff",
    "xkcd:terracotta": "#ca6641",
    "xkcd:aqua blue": "#02d8e9",
    "xkcd:sage green": "#88b378",
    "xkcd:blood red": "#980002",
    "xkcd:deep pink": "#cb0162",
    "xkcd:grass": "#5cac2d",
    "xkcd:moss": "#769958",
    "xkcd:pastel blue": "#a2bffe",
    "xkcd:bluish green": "#10a674",
    "xkcd:green blue": "#06b48b",
    "xkcd:dark tan": "#af884a",
    "xkcd:greenish blue": "#0b8b87",
    "xkcd:pale orange": "#ffa756",
    "xkcd:vomit": "#a2a415",
    "xkcd:forrest green": "#154406",
    "xkcd:dark lavender": "#856798",
    "xkcd:dark violet": "#34013f",
    "xkcd:purple blue": "#632de9",
    "xkcd:dark cyan": "#0a888a",
    "xkcd:olive drab": "#6f7632",
    "xkcd:pinkish": "#d46a7e",
    "xkcd:cobalt": "#1e488f",
    "xkcd:neon purple": "#bc13fe",
    "xkcd:light turquoise": "#7ef4cc",
    "xkcd:apple green": "#76cd26",
    "xkcd:dull green": "#74a662",
    "xkcd:wine": "#80013f",
    "xkcd:powder blue": "#b1d1fc",
    "xkcd:off white": "#ffffe4",
    "xkcd:electric blue": "#0652ff",
    "xkcd:dark turquoise": "#045c5a",
    "xkcd:blue purple": "#5729ce",
    "xkcd:azure": "#069af3",
    "xkcd:bright red": "#ff000d",
    "xkcd:pinkish red": "#f10c45",
    "xkcd:cornflower blue": "#5170d7",
    "xkcd:light olive": "#acbf69",
    "xkcd:grape": "#6c3461",
    "xkcd:greyish blue": "#5e819d",
    "xkcd:purplish blue": "#601ef9",
    "xkcd:yellowish green": "#b0dd16",
    "xkcd:greenish yellow": "#cdfd02",
    "xkcd:medium blue": "#2c6fbb",
    "xkcd:dusty rose": "#c0737a",
    "xkcd:light violet": "#d6b4fc",
    "xkcd:midnight blue": "#020035",
    "xkcd:bluish purple": "#703be7",
    "xkcd:red orange": "#fd3c06",
    "xkcd:dark magenta": "#960056",
    "xkcd:greenish": "#40a368",
    "xkcd:ocean blue": "#03719c",
    "xkcd:coral": "#fc5a50",
    "xkcd:cream": "#ffffc2",
    "xkcd:reddish brown": "#7f2b0a",
    "xkcd:burnt sienna": "#b04e0f",
    "xkcd:brick": "#a03623",
    "xkcd:sage": "#87ae73",
    "xkcd:grey green": "#789b73",
    "xkcd:white": "#ffffff",
    "xkcd:robin's egg blue": "#98eff9",
    "xkcd:moss green": "#658b38",
    "xkcd:steel blue": "#5a7d9a",
    "xkcd:eggplant": "#380835",
    "xkcd:light yellow": "#fffe7a",
    "xkcd:leaf green": "#5ca904",
    "xkcd:light grey": "#d8dcd6",
    "xkcd:puke": "#a5a502",
    "xkcd:pinkish purple": "#d648d7",
    "xkcd:sea blue": "#047495",
    "xkcd:pale purple": "#b790d4",
    "xkcd:slate blue": "#5b7c99",
    "xkcd:blue grey": "#607c8e",
    "xkcd:hunter green": "#0b4008",
    "xkcd:fuchsia": "#ed0dd9",
    "xkcd:crimson": "#8c000f",
    "xkcd:pale yellow": "#ffff84",
    "xkcd:ochre": "#bf9005",
    "xkcd:mustard yellow": "#d2bd0a",
    "xkcd:light red": "#ff474c",
    "xkcd:cerulean": "#0485d1",
    "xkcd:pale pink": "#ffcfdc",
    "xkcd:deep blue": "#040273",
    "xkcd:rust": "#a83c09",
    "xkcd:light teal": "#90e4c1",
    "xkcd:slate": "#516572",
    "xkcd:goldenrod": "#fac205",
    "xkcd:dark yellow": "#d5b60a",
    "xkcd:dark grey": "#363737",
    "xkcd:army green": "#4b5d16",
    "xkcd:grey blue": "#6b8ba4",
    "xkcd:seafoam": "#80f9ad",
    "xkcd:puce": "#a57e52",
    "xkcd:spring green": "#a9f971",
    "xkcd:dark orange": "#c65102",
    "xkcd:sand": "#e2ca76",
    "xkcd:pastel green": "#b0ff9d",
    "xkcd:mint": "#9ffeb0",
    "xkcd:light orange": "#fdaa48",
    "xkcd:bright pink": "#fe01b1",
    "xkcd:chartreuse": "#c1f80a",
    "xkcd:deep purple": "#36013f",
    "xkcd:dark brown": "#341c02",
    "xkcd:taupe": "#b9a281",
    "xkcd:pea green": "#8eab12",
    "xkcd:puke green": "#9aae07",
    "xkcd:kelly green": "#02ab2e",
    "xkcd:seafoam green": "#7af9ab",
    "xkcd:blue green": "#137e6d",
    "xkcd:khaki": "#aaa662",
    "xkcd:burgundy": "#610023",
    "xkcd:dark teal": "#014d4e",
    "xkcd:brick red": "#8f1402",
    "xkcd:royal purple": "#4b006e",
    "xkcd:plum": "#580f41",
    "xkcd:mint green": "#8fff9f",
    "xkcd:gold": "#dbb40c",
    "xkcd:baby blue": "#a2cffe",
    "xkcd:yellow green": "#c0fb2d",
    "xkcd:bright purple": "#be03fd",
    "xkcd:dark red": "#840000",
    "xkcd:pale blue": "#d0fefe",
    "xkcd:grass green": "#3f9b0b",
    "xkcd:navy": "#01153e",
    "xkcd:aquamarine": "#04d8b2",
    "xkcd:burnt orange": "#c04e01",
    "xkcd:neon green": "#0cff0c",
    "xkcd:bright blue": "#0165fc",
    "xkcd:rose": "#cf6275",
    "xkcd:light pink": "#ffd1df",
    "xkcd:mustard": "#ceb301",
    "xkcd:indigo": "#380282",
    "xkcd:lime": "#aaff32",
    "xkcd:sea green": "#53fca1",
    "xkcd:periwinkle": "#8e82fe",
    "xkcd:dark pink": "#cb416b",
    "xkcd:olive green": "#677a04",
    "xkcd:peach": "#ffb07c",
    "xkcd:pale green": "#c7fdb5",
    "xkcd:light brown": "#ad8150",
    "xkcd:hot pink": "#ff028d",
    "xkcd:black": "#000000",
    "xkcd:lilac": "#cea2fd",
    "xkcd:navy blue": "#001146",
    "xkcd:royal blue": "#0504aa",
    "xkcd:beige": "#e6daa6",
    "xkcd:salmon": "#ff796c",
    "xkcd:olive": "#6e750e",
    "xkcd:maroon": "#650021",
    "xkcd:bright green": "#01ff07",
    "xkcd:dark purple": "#35063e",
    "xkcd:mauve": "#ae7181",
    "xkcd:forest green": "#06470c",
    "xkcd:aqua": "#13eac9",
    "xkcd:cyan": "#00ffff",
    "xkcd:tan": "#d1b26f",
    "xkcd:dark blue": "#00035b",
    "xkcd:lavender": "#c79fef",
    "xkcd:turquoise": "#06c2ac",
    "xkcd:dark green": "#033500",
    "xkcd:violet": "#9a0eea",
    "xkcd:light purple": "#bf77f6",
    "xkcd:lime green": "#89fe05",
    "xkcd:grey": "#929591",
    "xkcd:sky blue": "#75bbfd",
    "xkcd:yellow": "#ffff14",
    "xkcd:magenta": "#c20078",
    "xkcd:light green": "#96f97b",
    "xkcd:orange": "#f97306",
    "xkcd:teal": "#029386",
    "xkcd:light blue": "#95d0fc",
    "xkcd:red": "#e50000",
    "xkcd:brown": "#653700",
    "xkcd:pink": "#ff81c0",
    "xkcd:blue": "#0343df",
    "xkcd:green": "#15b01a",
    "xkcd:purple": "#7e1e9c",
    "xkcd:gray teal": "#5e9b8a",
    "xkcd:purpley gray": "#947e94",
    "xkcd:light gray green": "#b7e1a1",
    "xkcd:reddish gray": "#997570",
    "xkcd:battleship gray": "#6b7c85",
    "xkcd:charcoal gray": "#3c4142",
    "xkcd:grayish teal": "#719f91",
    "xkcd:gray/green": "#86a17d",
    "xkcd:cool gray": "#95a3a6",
    "xkcd:dark blue gray": "#1f3b4d",
    "xkcd:bluey gray": "#89a0b0",
    "xkcd:greeny gray": "#7ea07a",
    "xkcd:bluegray": "#85a3b2",
    "xkcd:light blue gray": "#b7c9e2",
    "xkcd:gray/blue": "#647d8e",
    "xkcd:brown gray": "#8d8468",
    "xkcd:blue/gray": "#758da3",
    "xkcd:grayblue": "#77a1b5",
    "xkcd:dark gray blue": "#29465b",
    "xkcd:grayish": "#a8a495",
    "xkcd:light gray blue": "#9dbcd4",
    "xkcd:pale gray": "#fdfdfe",
    "xkcd:warm gray": "#978a84",
    "xkcd:gray pink": "#c3909b",
    "xkcd:medium gray": "#7d7f7c",
    "xkcd:pinkish gray": "#c8aca9",
    "xkcd:brownish gray": "#86775f",
    "xkcd:purplish gray": "#7a687f",
    "xkcd:grayish pink": "#c88d94",
    "xkcd:grayish brown": "#7a6a4f",
    "xkcd:steel gray": "#6f828a",
    "xkcd:purple gray": "#866f85",
    "xkcd:gray brown": "#7f7053",
    "xkcd:green gray": "#77926f",
    "xkcd:bluish gray": "#748b97",
    "xkcd:slate gray": "#59656d",
    "xkcd:gray purple": "#826d8c",
    "xkcd:greenish gray": "#96ae8d",
    "xkcd:grayish purple": "#887191",
    "xkcd:grayish green": "#82a67d",
    "xkcd:grayish blue": "#5e819d",
    "xkcd:gray green": "#789b73",
    "xkcd:light gray": "#d8dcd6",
    "xkcd:blue gray": "#607c8e",
    "xkcd:dark gray": "#363737",
    "xkcd:gray blue": "#6b8ba4",
    "xkcd:gray": "#929591",
    "aliceblue": "#f0f8ff",
    "antiquewhite": "#faebd7",
    "aqua": "#00ffff",
    "aquamarine": "#7fffd4",
    "azure": "#f0ffff",
    "beige": "#f5f5dc",
    "bisque": "#ffe4c4",
    "black": "#000000",
    "blanchedalmond": "#ffebcd",
    "blue": "#0000ff",
    "blueviolet": "#8a2be2",
    "brown": "#a52a2a",
    "burlywood": "#deb887",
    "cadetblue": "#5f9ea0",
    "chartreuse": "#7fff00",
    "chocolate": "#d2691e",
    "coral": "#ff7f50",
    "cornflowerblue": "#6495ed",
    "cornsilk": "#fff8dc",
    "crimson": "#dc143c",
    "cyan": "#00ffff",
    "darkblue": "#00008b",
    "darkcyan": "#008b8b",
    "darkgoldenrod": "#b8860b",
    "darkgray": "#a9a9a9",
    "darkgreen": "#006400",
    "darkgrey": "#a9a9a9",
    "darkkhaki": "#bdb76b",
    "darkmagenta": "#8b008b",
    "darkolivegreen": "#556b2f",
    "darkorange": "#ff8c00",
    "darkorchid": "#9932cc",
    "darkred": "#8b0000",
    "darksalmon": "#e9967a",
    "darkseagreen": "#8fbc8f",
    "darkslateblue": "#483d8b",
    "darkslategray": "#2f4f4f",
    "darkslategrey": "#2f4f4f",
    "darkturquoise": "#00ced1",
    "darkviolet": "#9400d3",
    "deeppink": "#ff1493",
    "deepskyblue": "#00bfff",
    "dimgray": "#696969",
    "dimgrey": "#696969",
    "dodgerblue": "#1e90ff",
    "firebrick": "#b22222",
    "floralwhite": "#fffaf0",
    "forestgreen": "#228b22",
    "fuchsia": "#ff00ff",
    "gainsboro": "#dcdcdc",
    "ghostwhite": "#f8f8ff",
    "gold": "#ffd700",
    "goldenrod": "#daa520",
    "gray": "#808080",
    "green": "#008000",
    "greenyellow": "#adff2f",
    "grey": "#808080",
    "honeydew": "#f0fff0",
    "hotpink": "#ff69b4",
    "indianred": "#cd5c5c",
    "indigo": "#4b0082",
    "ivory": "#fffff0",
    "khaki": "#f0e68c",
    "lavender": "#e6e6fa",
    "lavenderblush": "#fff0f5",
    "lawngreen": "#7cfc00",
    "lemonchiffon": "#fffacd",
    "lightblue": "#add8e6",
    "lightcoral": "#f08080",
    "lightcyan": "#e0ffff",
    "lightgoldenrodyellow": "#fafad2",
    "lightgray": "#d3d3d3",
    "lightgreen": "#90ee90",
    "lightgrey": "#d3d3d3",
    "lightpink": "#ffb6c1",
    "lightsalmon": "#ffa07a",
    "lightseagreen": "#20b2aa",
    "lightskyblue": "#87cefa",
    "lightslategray": "#778899",
    "lightslategrey": "#778899",
    "lightsteelblue": "#b0c4de",
    "lightyellow": "#ffffe0",
    "lime": "#00ff00",
    "limegreen": "#32cd32",
    "linen": "#faf0e6",
    "magenta": "#ff00ff",
    "maroon": "#800000",
    "mediumaquamarine": "#66cdaa",
    "mediumblue": "#0000cd",
    "mediumorchid": "#ba55d3",
    "mediumpurple": "#9370db",
    "mediumseagreen": "#3cb371",
    "mediumslateblue": "#7b68ee",
    "mediumspringgreen": "#00fa9a",
    "mediumturquoise": "#48d1cc",
    "mediumvioletred": "#c71585",
    "midnightblue": "#191970",
    "mintcream": "#f5fffa",
    "mistyrose": "#ffe4e1",
    "moccasin": "#ffe4b5",
    "navajowhite": "#ffdead",
    "navy": "#000080",
    "oldlace": "#fdf5e6",
    "olive": "#808000",
    "olivedrab": "#6b8e23",
    "orange": "#ffa500",
    "orangered": "#ff4500",
    "orchid": "#da70d6",
    "palegoldenrod": "#eee8aa",
    "palegreen": "#98fb98",
    "paleturquoise": "#afeeee",
    "palevioletred": "#db7093",
    "papayawhip": "#ffefd5",
    "peachpuff": "#ffdab9",
    "peru": "#cd853f",
    "pink": "#ffc0cb",
    "plum": "#dda0dd",
    "powderblue": "#b0e0e6",
    "purple": "#800080",
    "rebeccapurple": "#663399",
    "red": "#ff0000",
    "rosybrown": "#bc8f8f",
    "royalblue": "#4169e1",
    "saddlebrown": "#8b4513",
    "salmon": "#fa8072",
    "sandybrown": "#f4a460",
    "seagreen": "#2e8b57",
    "seashell": "#fff5ee",
    "sienna": "#a0522d",
    "silver": "#c0c0c0",
    "skyblue": "#87ceeb",
    "slateblue": "#6a5acd",
    "slategray": "#708090",
    "slategrey": "#708090",
    "snow": "#fffafa",
    "springgreen": "#00ff7f",
    "steelblue": "#4682b4",
    "tan": "#d2b48c",
    "teal": "#008080",
    "thistle": "#d8bfd8",
    "tomato": "#ff6347",
    "turquoise": "#40e0d0",
    "violet": "#ee82ee",
    "wheat": "#f5deb3",
    "white": "#ffffff",
    "whitesmoke": "#f5f5f5",
    "yellow": "#ffff00",
    "yellowgreen": "#9acd32",
    "tab:blue": "#1f77b4",
    "tab:orange": "#ff7f0e",
    "tab:green": "#2ca02c",
    "tab:red": "#d62728",
    "tab:purple": "#9467bd",
    "tab:brown": "#8c564b",
    "tab:pink": "#e377c2",
    "tab:gray": "#7f7f7f",
    "tab:olive": "#bcbd22",
    "tab:cyan": "#17becf",
    "tab:grey": "#7f7f7f",
    "b": "#0000ff",
    "g": "#008000",
    "r": "#ff0000",
    "c": "#00bfbf",
    "m": "#bf00bf",
    "y": "#bfbf00",
    "k": "#000000",
    "w": "#ffffff",
}


# Copied from old_figure.colors
def parse_number_colors(text):
    """
    Check if a string contains 3 or 4 floats/ints representing a rgb(a) color.

    Parameters
    ----------
    text : unicode

    Returns
    -------
    is_float : np.ndarray or None
    is_int : np.ndarray or None
    """
    # rgb colors
    ex = r"(?: (?: \d* \. \d+ ) | (?: \d+ \.? ) )"
    rx = re.compile(ex, re.VERBOSE)
    numbers = rx.findall(text)
    is_float = np.float_(numbers)
    if (is_float is None or np.any(is_float > 1.) or
            len(is_float) not in [3, 4]):
        is_float = None
    try:
        is_int = np.int_(numbers)
        if (is_int is None or np.any(is_int > 255) or
                len(is_int) not in [3, 4] or '.' in text):
            is_int = None
    except ValueError:
        is_int = None
    return is_float, is_int


def _is_float(v):
    try:
        float(v)
    except Exception:
        return False
    else:
        return True


def _is_bool(v):
    return v.lower() in ['true', 'false']


def _to_bool(v):
    return v.lower() == 'true'


def _update_value(k, v, axes_info):
    compiles = True
    try:
        compile(v, '<string>', 'eval')
    except Exception:
        compiles = False
    python_reasons = []
    python_reasons.append(re.match(r'\b(table|arg)\b', v))
    python_reasons.append(k in _py_only_props)
    python_reasons.append(k in _text_to_float and not _is_float(v))
    python_reasons.append(k in _text_to_bool and not _is_bool(v))
    if compiles and any(python_reasons):
        # TODO: This could still be a column name or a simple value!
        v = re.sub(r'\btable\b', 'arg', v)
        return k, (v, 'py')
    else:
        if k == 'zorder':
            # zorder properties changed from float to int
            v = str(int(float(v)))
        elif k == 'loc':
            # The value 'right' was removed from legend locations, use the
            # equivalent 'center right' instead.
            if v == 'right':
                v = 'center right'
        elif k == 'manage_ticks':
            # This property (only used in box plots) has been removed and is
            # now inferred instead
            k = None
        elif k == 'rot_bin_labels':
            # This property (only used in bar and box plots) was moved to each
            # axis. Save its value for later.
            if axes_info is not None:
                axes_info[k] = v
            k = None
        elif k == 'frame':
            # This property (only used in pie charts) was removed. Save its
            # value for later.
            if axes_info is not None:
                axes_info['pie_frame'] = v
            k = None
        elif k == 'vert':
            # vert property (only used in box plots) was changed to a
            # property called orientation
            k = 'orientation'
            v = 'Vertical' if _to_bool(v) else 'Horizontal'
        elif k == 'histtype':
            # histtype property (only used in histograms) was changed into the
            # boolean property called edges
            k = 'edges'
            v = str(v == 'bar')
        elif k in ('color', 'fontcolor', 'facecolor', 'edgecolor'):
            # Old figure node allowed many ways of specifying colors. In new
            # node it is restricted to hex notation.
            if v in mpl_colornames:
                v = mpl_colornames[v]
            else:
                floats, ints = parse_number_colors(v)
                if floats is not None:
                    ints = np.int_(floats*255)
                if ints is not None:
                    v = '#' + ''.join("{:0>2x}".format(i) for i in ints)
        return k, (v, 'value')


def _walk_tree(d, axes_info=None):
    if isinstance(d, list):
        return [_walk_tree(v, axes_info=axes_info) for v in d]
    elif isinstance(d, dict):
        new_d = {}
        for k, v in d.items():
            if k == 'axes':
                # Sometimes we need to modify the axes dictionary because of
                # something in a plot. That is communicated via axes_info and
                # performed here:
                res = []
                for axes in v:
                    axes_info = {}
                    new_axes = _walk_tree(axes, axes_info=axes_info)

                    # This property (only used in bar and box plots) was moved
                    # to each axis
                    rot = axes_info.get('rot_bin_labels')
                    if rot is not None:
                        new_axes['xaxis']['rot_tick_labels'] = (rot, 'value')

                    # Pie charts no longer automatically hide frame and ticks
                    # and set equal aspect ratio.
                    pie = axes_info.get('pie')
                    if pie is not None:
                        new_axes.setdefault('aspect', ('equal', 'value'))
                        hide_frame = True
                        if _to_bool(axes_info.get('pie_frame', 'false')):
                            # Only keep the frame and ticks visible if the
                            # property 'frame' was set to True on the pie
                            # chart.
                            hide_frame = False
                        if hide_frame:
                            new_axes.setdefault('frameon', ('False', 'value'))
                            new_axes['xaxis'].setdefault(
                                'visible', ('False', 'value'))
                            new_axes['yaxis'].setdefault(
                                'visible', ('False', 'value'))
                    res.append(new_axes)
                new_d[k] = res

            elif isinstance(v, (tuple, list, dict)):
                new_d[k] = _walk_tree(v, axes_info=axes_info)

            elif k == 'type':
                # Axes level no longer needs a type in new version
                if v != 'axes':
                    # type leaves do not need a 'value'/'py' specifier
                    new_d[k] = v
                    if v == 'pie':
                        if axes_info is not None:
                            # There is a pie chart in this axes. Save that info
                            # for later.
                            axes_info['pie'] = True
                continue

            elif k == 'lim':
                # xlim/ylim properties were split into min and max properties
                m = re.match(r'(?:\(|\[)(.*),(.*)(?:\]|\))', v)
                if not m:
                    continue
                min_, max_ = m.groups()
                min_, max_ = min_.strip(), max_.strip()
                if min_ != 'None':
                    k, v = _update_value('min', min_, axes_info)
                    new_d[k] = v
                if max_ != 'None':
                    k, v = _update_value('max', max_, axes_info)
                    new_d[k] = v
            else:
                k, v = _update_value(k, v, axes_info)
                if k is not None:
                    new_d[k] = v
        return new_d
    else:
        return d


def _update_figure_params(params):
    from sylib.old_figure import util as old_fig_util

    # The parameters are now represented as a tree directly
    old_tree = old_fig_util.parse_configuration(params)
    # Figure level is the new root level
    old_tree = old_tree['figure']

    return _walk_tree(old_tree)


class OldFigureUpdateParameters(migrations.UpdateParametersMigration):
    nodeid = 'org.sysess.sympathy.visualize.figuretabletreegui'

    def updated_definition(self):
        parameters = synode.parameters()
        parameters.set_string(
            'parameters', value='[]',
            label='GUI', description='Configuration window')
        return parameters

    def update_parameters(self, old_params):
        # Old nodes have their parameters stored as a list, but nowadays we
        # json-encode that list into a string instead.
        if old_params['parameters'].type == 'list':
            parameters_list = old_params['parameters'].list
            del old_params['parameters']
            old_params.set_string(
                'parameters', value=json.dumps(parameters_list))


class FigureFromAnyWithTreeView(migrations.NodeMigration):
    nodeid = 'org.sysess.sympathy.visualize.figuretabletreegui'
    from_version = migrations.updated_version
    to_version = migrations.updated_version

    def forward_status(self):
        return (migrations.Imperfect,
                "This migration has some limitations. Please double check "
                "that the new node produces the same result as the old one.")

    def forward_node(self):
        return dict(
            author='Benedikt Ziegler & Magnus Sandén',
            icon='figure.svg',
            name='Figure',
            description='Create a Figure from some data.',
            nodeid='org.sysess.sympathy.visualize.figure',
            tags=Tags(Tag.Visual.Figure),
            # related=['org.sysess.sympathy.visualize.figures',
            #          'org.sysess.sympathy.visualize.figuresubplot',
            #          'org.sysess.sympathy.visualize.figurecompressorgui'],

            inputs=Ports([
                Port.Custom('<a>', 'Input', name='input')]),
            outputs=Ports([
                Port.Figure('Output figure', name='figure', preview=True)]),
        )

    def forward_parameters(self, old_parameters):
        new_parameters = synode.parameters()
        new_parameters.set_json(
            'parameters', value={},
            description='The full configuration for this figure.')

        old_parameters = copy.deepcopy(old_parameters)

        new_parameters['parameters'].value = _update_figure_params(
            json.loads(old_parameters['parameters'].value))
        return new_parameters

    def forward_ports(self, old_input_ports, old_output_ports):
        new_output_ports = [('figure', 0), None]
        return old_input_ports, new_output_ports


class OldFiguresUpdateParameters(OldFigureUpdateParameters):
    nodeid = 'org.sysess.sympathy.visualize.figurestablestreegui'


class FiguresFromAnyListWithTreeView(FigureFromAnyWithTreeView):
    nodeid = 'org.sysess.sympathy.visualize.figurestablestreegui'

    def forward_node(self):
        return dict(
            author='Benedikt Ziegler & Magnus Sandén',
            icon='figure.svg',
            name='Figures',
            description='Create a Figure from some data.',
            nodeid='org.sysess.sympathy.visualize.figures',
            tags=Tags(Tag.Visual.Figure),
            # related=['org.sysess.sympathy.visualize.figures',
            #          'org.sysess.sympathy.visualize.figuresubplot',
            #          'org.sysess.sympathy.visualize.figurecompressorgui'],

            inputs=Ports([
                Port.Custom('[<a>]', 'Input', name='input')]),
            outputs=Ports([
                Port.Figures('Output figure', name='figure', preview=True)]),
        )

    def forward_ports(self, old_input_ports, old_output_ports):
        new_input_ports = [('input', 0)]
        new_output_ports = [('figure', 0), None]
        return new_input_ports, new_output_ports
