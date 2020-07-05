import re
import unittest


class SMC_test(unittest.TestCase):
    def test_speed_read(self):
        out_text = "  F0Mx  [fpe2]  4500.00 (bytes 46 50)"
        bytes_reg = '.*bytes (.*)\)'

        low, high = re.search(bytes_reg, out_text).group(1).split()
        speed = ((int(low, 16) * 256) + int(high, 16)) / 4
        
        self.assertEqual(float('4500.00'), float(speed))
    
    def test_temp_read(self):
        out_text = "  TC0D  [sp78]  59.375 (bytes 3b 60)"
        bytes_reg = '.*bytes (.*)\)'

        low, high = re.search(bytes_reg, out_text).group(1).split()
        temp = ((int(low, 16) * 256) + int(high, 16)) / 4 / 64
        
        self.assertEqual(float('59.375'), float(temp))


if __name__ == '__main__':
    unittest.main()

