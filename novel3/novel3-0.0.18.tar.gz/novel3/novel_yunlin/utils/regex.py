import re


class RegexUtils:
    @classmethod
    def regex_search(cls, content, pattern, index=1):
        try:
            pattern = re.compile(r'{0}'.format(pattern))
            return pattern.search(content).group(index)
        except Exception as e:
            return None


if __name__ == '__main__':
    content = "1234567"
    pattern = r"(.+?)67"
    text = RegexUtils.regex_search(content, pattern, 1)
    print(text)
