import json
import unittest

from src.files_management import *

loras = [{"loraid": 1, "slaves": [1]}, {"loraid": 2, "slaves": [1, 2]}]
test_post_list = ['000101', '000201', '000202']

x


class TestFiles(unittest.TestCase):
    """
    Test that we can parse files
    """
    def test_energy_boot(self):
        test_path = "test/test_files/test_energy.json"
        f_energy_boot(loras, test_path)
        with open(test_path) as file:
            test_dic = json.load(file)
            exp_dic = {"000101": 0, "000201": 0, "000202": 0}
            self.assertEqual(test_dic, exp_dic, "Must be equal")

    def test_post_boot(self):
        test_path = "test/test_files/test_post.json"
        f_post_boot(loras, test_path)
        with open(test_path) as file:
            test_dic = json.load(file)
            test_array = test_dic["updates"]
            test_list = []
            for meter in test_array:
                test_list.append(meter["meterid"])
            self.assertEqual(test_list, test_post_list)


if __name__ == '__main__':
    unittest.main()
