import subprocess
import os

def test_request():
    p = subprocess.run(['prop', 'https://www.example.com'])
    assert p.returncode == 0