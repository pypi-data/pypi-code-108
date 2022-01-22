import sys

limit_up_percent = 10
limit_down_percent = -10

# Ref: https://davidhuang1219.pixnet.net/blog/post/330857095-%E5%8F%B0%E8%82%A1%E4%BA%A4%E6%98%93%E6%99%82%E9%96%93%E3%80%81%E6%BC%B2%E8%B7%8C%E5%B9%85%E9%99%90%E5%88%B6%E3%80%81%E5%8D%87%E9%99%8D%E5%96%AE%E4%BD%8D
price_base_map =[
    {
        'price': 10,
        'base': 0.01
    },
    {
        'price': 50,
        'base': 0.05
    },
    {
        'price': 100,
        'base': 0.1
    },
    {
        'price': 500,
        'base': 0.5
    },
    {
        'price': 1000,
        'base': 1
    },
    {
        'price': sys.maxsize,
        'base': 5
    }
]