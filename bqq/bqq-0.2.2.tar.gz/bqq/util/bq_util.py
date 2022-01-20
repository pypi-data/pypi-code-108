def size_fmt(num: int) -> str:
    for unit in ["B", "KiB", "MiB", "GiB", "TiB", "PiB"]:
        if abs(num) < 1024:
            size = round(num, 1)
            return f"{size} {unit}"
        else:
            num /= 1024


def price_fmt(num: int) -> str:
    tb = num / 1e12
    price = tb * 5
    price_round = "{:.2f}".format(round(price, 2))
    if price < 0.01 and price != 0:
        price_round = f"+{price_round}"
    return f"{price_round} $"
