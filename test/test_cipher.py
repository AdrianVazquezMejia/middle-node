import unittest

from src.cipher import *

key = b'\xff\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f\xff\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'
iv = b'\xff\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'


class TestCipher(unittest.TestCase):

    def test_cipher(self):
        """
        Test that it can cipher and decipher
        """
        data = [1, 2, 3]
        result = encrypt_md(data, "CFB")
        self.assertEqual(result, [105, 97, 179], "Must be equal")

    def test_decipher(self):
        data = [105, 97, 179]
        result = decrypt_md(data, "CFB")
        self.assertEqual(list(result), [1, 2, 3], "Must be equal")


if __name__ == '__main__':
    unittest.main()
