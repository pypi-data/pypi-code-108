import pandas as pd

def required_package():
    packate_frame = pd.DataFrame(columns=['Application', 'Installation', 'Example'],
            data=[
                ['Natural Language Processing', 'pip install konlpy', ''],
                ['Natural Language Processing', 'pip install git+https://github.com/haven-jeon/PyKoSpacing.git', ''],
                ['Natural Language Processing', 'pip install git+https://github.com/ssut/py-hanspell.git', ''],
                ['Natural Language Processing', 'pip install soynlp', ''],
                ['Financial Engineering', 'pip install tabula-py', ''],
                ['Financial Engineering', 'pip install monthdelta', ''],
                ])
    return package_frame
