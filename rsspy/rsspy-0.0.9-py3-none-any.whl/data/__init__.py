from authc import authc
accs = authc()

WECHAT_PUBLIC = {
    'almosthuman': {
        'main_url': accs['werss_almosthuman'],
        'source': '机器之心',
        'redis_subkey': 'almosthuman',
    },
    'yuntoutiao': {
        'main_url': accs['werss_yuntoutiao'],
        'source': '云头条',
        'redis_subkey': 'yuntoutiao',
    },
    'aifront': {
        'main_url': accs['werss_aifront'],
        'source': 'AI前线',
        'redis_subkey': 'aifront',
    },
    'huxiu': {
        'main_url': 'https://www.wxkol.com/show/huxiu_com.html',
        'source': '虎嗅网',
        'redis_subkey': 'huxiu',
    },
    'infoq': {
        'main_url': 'https://www.wxkol.com/show/infoqchina.html',
        'source': 'InfoQ',
        'redis_subkey': 'infoq',
    },
}

TELEGRAM = {'bot_name': 'hema_bot', 'channel_name': 'global_news_podcast'}
