import json
import os
from pathlib import Path


def save_to_json_file(data, filename):
    """Save to JSON file

    :data: data from scrapersave
    :filename: filename to save in
    :returns: None

    """
    directory = os.path.dirname(filename)
    Path(directory).mkdir(parents=True, exist_ok=True)

    with open(filename, 'w', encoding='utf8') as json_file:
        json.dump(data, json_file, indent=4, ensure_ascii=False)
    return
