import unittest
from src.centralnode import *

class TestCentralNode(unittest.TestCase):
    """
    Test main methods
    """
    
    def test_config_frame(self):
        node = centralnode("test/test_files/test_config.json")
        test_frame = node.config_trama()
        self.assertEqual(test_frame,[1, 0, 1, 13, 165, 165, 108, 64, 18, 7, 0, 0, 1, 1, 0, 3, 0, 55] , "Must be equal")
    
if __name__ == "__main__":
    unittest.main()
        