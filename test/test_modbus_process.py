import unittest

from src.modbus_process import *


class TestModbus(unittest.TestCase):
    """
    Test Modbus processing
    """ 

    def test_modbus_adu(self):
        adu = get_modbus_adu(1, 4, 0, 2)
        self.assertEqual(adu, [1, 4, 0, 0, 0, 2, 113, 203], "Must be equal")
    
    def test_modbus_parse(self):
        frame = [1, 4, 4, 0, 6, 0, 5, 219, 134]
        data = parse_modbus(bytes(frame))
        self.assertEqual(data, [393221], "Must be equal")


if __name__ == "__main__":
    unittest.main()
