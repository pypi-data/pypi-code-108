import unittest
from parameterized import parameterized

from marlowe_ui.postprocess_lark import initial_config

class TestInitialConfig(unittest.TestCase):
    def setUp(self):
        pass

    # input files are at final_sequex_examples/
    @parameterized.expand([
        ('''\
Primary projectiles to be generated:      10
Primary projectiles per group:             2
Projectile groups to be generated:         5
''',
{
    'Total Projectiles': 10,
    'Projectiles per Group': 2,
    'Total Groups': 5,
    'TIM_7': False }),
        ('''\
Primary projectiles to be generated:   6000
''',
{
    'Total Projectiles': 6000,
    'Projectiles per Group': 1,
    'Total Groups': 6000,
    'TIM_7': True })
])
    def test_cascade_summary(self, text, output):
        result = initial_config.parse(text)
        self.assertEqual(result, output)
