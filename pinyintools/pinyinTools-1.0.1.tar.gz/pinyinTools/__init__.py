try:
    from . import first_letter
    from . import key_type
    from . import usful_pinyin_packages
except ImportError:
    from pinyinTools import first_letter
    from pinyinTools import key_type
    from pinyinTools import usful_pinyin_packages
if __name__ == '__main__':
    print(first_letter, key_type, usful_pinyin_packages)
