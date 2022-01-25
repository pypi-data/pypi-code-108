from pathlib import Path

from .load import img2dict


def test_img2dict():
    example_jpg = Path(__file__).parent / 'example.jpg'
    d = img2dict(example_jpg)
    assert d['_name'] == 'example.jpg'
    assert d['_path'].endswith('example.jpg')
    assert d['thumb'].startswith('data:image')
    assert d['GPS GPSLatitude'] == '[47, 40, 50492639/1000000]'
    assert d['GPS GPSLongitude'] == '[12, 8, 12246359/1000000]'
    assert d['Image GPSInfo'] == '672'
