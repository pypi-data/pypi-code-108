import subprocess
import tempfile
import os

def test_recursive():
    with tempfile.TemporaryDirectory() as temp:
        p = subprocess.run(['prop', '-aDo', temp, '-r', '-I', '10', '-np', '-M', '3', '-f', '%(num)d.%(ext)s', 'https://github.com/mino-38/'])
        assert p.returncode == 0 and len(os.listdir(temp))