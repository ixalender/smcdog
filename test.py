import re
import unittest
from smcdog import parse_speed, config


class SMCTest(unittest.TestCase):
    def test_speed_read(self):
        smc_out_text = "  F0Mx  [fpe2]  4500.00 (bytes 46 50)"
        speed = parse_speed(smc_out_text)
        
        self.assertEqual('4500', speed)
    
    def test_temp_read(self):
        out_text = "  TC0D  [sp78]  59.375 (bytes 3b 60)"
        bytes_reg = '.*bytes (.*)\)'

        low, high = re.search(bytes_reg, out_text).group(1).split()
        temp = ((int(low, 16) * 256) + int(high, 16)) / 4 / 64
        
        self.assertEqual(float('59.375'), float(temp))


class SettingsTest(unittest.TestCase):
    def test_settings_load(self):
        self.assertEqual(4500, config('./fixtures/test.conf').speed)


if __name__ == '__main__':
    unittest.main()

