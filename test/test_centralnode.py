from unittest import mock
import unittest

from src.centralnode import *


class TestNode(centralnode):

    def overwrite(self):
        self.ser = mock.Mock()
        self.ser.read = mock.Mock(return_value="111111111111111100001".encode('utf-8'))

class TestCentralNode(unittest.TestCase):
    """
    Test main methods
    """  

    def test_config_frame(self):
        node = centralnode("test/test_files/test_config.json")
        test_frame = node.config_trama()
        exp = [1, 0, 1, 13, 165, 165, 108, 64, 18, 7, 0, 0, 1, 1, 0, 3, 0, 55]
        self.assertEqual(test_frame, exp, "Must be equal")

    def test_send(self):
        node = centralnode("test/test_files/test_config.json")
        test_frame = node.build_send_frame([1, 2, 3], 2)
        exp =  [5, 0, 1, 14, 0, 2, 0, 7, 1, 8, 1, 2, 3, 6]
        self.assertEqual(test_frame, exp, "Must be equal")  

    def test_receive(self):
        node = TestNode("test/test_files/test_config.json")
        node.overwrite()
        node.expected_size = 21
        self.assertEqual(node.receive(), b'0000', "Must be equal")     

if __name__ == "__main__":
    unittest.main()

