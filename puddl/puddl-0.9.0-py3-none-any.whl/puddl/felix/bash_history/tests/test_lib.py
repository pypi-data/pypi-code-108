from pathlib import Path
from unittest import TestCase

from puddl.felix.bash_history.lib import iter_bash_history


class Test(TestCase):
    HERE = Path(__file__).parent
    MULTILINE = """\
cat <<EOF > /tmp/hello
world
EOF\
"""

    def test_hist2dict(self):
        path = self.HERE / 'example.bash_history'
        with path.open() as f:
            actual = list(iter_bash_history(f))
        expected = [
            (1585254366, self.MULTILINE),
            (1585254441, 'tail ~/.bash_history'),
            (1585254727, "# this is a comment\necho and it's valid."),
        ]
        self.assertEqual(expected, actual)
