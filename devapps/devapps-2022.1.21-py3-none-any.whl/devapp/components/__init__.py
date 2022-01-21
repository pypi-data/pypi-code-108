def VimEnv(p):
    class Vim(p):
        runtime = 'user'
        filesystem = {
            'name': 'vimblack',
            'type': 'conda_env',
            'channel': 'https://my_company.com/pub/conda_axchange/channel',
            'packages': ['vim', 'vimblackhome'],
        }

    return Vim
