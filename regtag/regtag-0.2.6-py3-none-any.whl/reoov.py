import os

vi_chars = set(list(
    "àảãáạăằẳẵẴắẮặẶâÂầẦẩẨẫẪấẤậẬđĐèÈẻẺẽẼéÉẹẸêÊềỀểỂễỄếẾệỆìÌỉỈĩĨíÍịỊòÒỏỎõÕóÓôÔồỒổỔỗỖốỐộỘơƠờỜởỞỡỠớỚợỢùÙủỦũŨúÚụưƯừỪửỬữỮứỨựỰỳỲỷỶỹỸýÝ".lower()))

# non_oov_chars = set(list('/-'))

vi_dict = None


def format_word(text):
    text = text.lower()
    # text = text.replace('-', ' ')
    return text


def load_dictionary(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        words = file.read().strip().split('\n')
    word_dict = []
    for word in words:
        word_formated = format_word(word)
        # word_dict.append(word_formated)
        word_dict.extend(word_formated.split())
    word_dict.extend(list('".,?!@#$%^&*()_-+=\';:<>/`'))
    return set(word_dict)


def check_oov_word(word):
    global vi_dict
    if vi_dict is None:
        vi_dict = load_dictionary(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'vidict.txt'))

    if format_word(word) in vi_dict:
        return False
    if len(set(list(word)).intersection(vi_chars)) > 0:
        return False

    return True