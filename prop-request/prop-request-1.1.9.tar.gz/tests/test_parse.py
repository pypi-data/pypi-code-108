import subprocess
import tempfile
from pprint import pprint as print
def test_parse():
    answer = '<a href="./test1">test</a>\n\n<img src="./test2"/>'
    code = answer+'\n<p>test</p>'
    with tempfile.NamedTemporaryFile(suffix='.html', mode='w+') as f:
        f.write(code)
        f.flush()
        p = subprocess.run(['prop', '-p', f.name, '-s', 'tags=a,img'], stdout=subprocess.PIPE)
    assert p.returncode == 0 and p.stdout.decode().strip() == answer