class FormatError(Exception):
    ...


class ClearText:
    def clear_price(self, price: str) -> float:
        price = self.clear_text(price).replace(',', '.')
        try:
            return float(price)
        except:
            price = ''.join([i for i in price if i in ['01234567890.']])
        return float(price)

    @staticmethod
    def clear_text(text: str) -> str:
        if type(text) is not str:
            raise FormatError(f'Ожидается str, получен {type(text)}')
        text = text.replace('\t', '').replace('  ', '').replace('\n', '').lstrip().rstrip()
        return text
