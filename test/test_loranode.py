import unittest

from src.centralnode import *

test_dic = { 
        "loraid":2,
        "slaves":[1, 2, 3, 4, 5, 6]
        }


class TestLoraNode(unittest.TestCase):
    """
    Test the loranode members
    """

    def test_init(self):
        test_dic["slaves"] = 10 * test_dic["slaves"]
        test_lora = loranode(test_dic)
        self.assertEqual(test_lora.lastpollsize, 8, "Must be equal")

    def test_quantity_poll(self):
        test_lora = loranode(test_dic)
        n = test_lora.quantity_poll()
        self.assertEqual(n, 3, "Must be equal")


if __name__ == "__main__":
    unittest.main()
