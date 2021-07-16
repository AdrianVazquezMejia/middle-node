"""
Created on Jul 9, 2021

@author: adrian
"""
import unittest

import sqlite3

from src.sqlite_manager import *


class TestUpdate(unittest.TestCase):
    
    def setUp(self):

        conn = sqlite3.connect("meter_db.sqlite")
        cur = conn.cursor()
        cur.execute('DROP TABLE IF EXISTS meter_table')
        cur.execute('CREATE TABLE meter_table (meter_id TEXT, energy INTEGER,date TEXT, status BOOLEAN)')
        cur.execute('INSERT INTO meter_table (meter_id, energy,date, status) VALUES (?, ?, ?, ? )', ("00fe00", 0, "2021-06-26 18:41:23.580757", True))
        cur.execute('INSERT INTO meter_table (meter_id, energy,date, status) VALUES (?, ?, ?, ? )', ("00ff01", 0, "2021-06-26 18:41:23.580757", True))
        cur.execute('INSERT INTO meter_table (meter_id, energy,date, status) VALUES (?, ?, ?, ? )', ("00ff02", 0, "2021-06-26 18:41:23.580757", True))
        cur.execute('INSERT INTO meter_table (meter_id, energy,date, status) VALUES (?, ?, ?, ? )', ("00ff03", 0, "2021-06-26 18:41:23.580757", True))
        cur.execute('INSERT INTO meter_table (meter_id, energy,date, status) VALUES (?, ?, ?, ? )', ("00ff04", 0, "2021-06-26 18:41:23.580757", True))
        conn.commit()
        cur.close()

    def testUpdateExistingMeter(self):

        expected_data = 1234
        update_date_base("00ff01", expected_data)
        conn = sqlite3.connect("meter_db.sqlite")
        cur = conn.cursor()
        cur.execute('SELECT * FROM meter_table WHERE meter_id = ?', ("00fe00",))
        actual_data = cur.fetchone()[1]
        self.assertEqual(actual_data, expected_data, "Should be equal")
        cur.close()

    def testUpdateNonExistingMeter(self):

        expected_data = 1234
        update_date_base("00fe01", expected_data)
        conn = sqlite3.connect("meter_db.sqlite")
        cur = conn.cursor()
        cur.execute('SELECT * FROM meter_table WHERE meter_id = ?', ("00ff00",))
        actual_data = cur.fetchone()      
        self.assertIsNone(actual_data, "Should be None")
        cur.close()

    def testSuccessReponse(self):

        data = 1234
        expected_response = 0
        actual_response = update_date_base("00ff01", data)
        self.assertEqual(actual_response, expected_response, "Should be equal")

    def testErorReponse(self):

        data = 1234
        expected_response = -1
        actual_response = update_date_base("00ff00", data)
        self.assertEqual(actual_response, expected_response, "Should be equal")


if __name__ == "__main__":
    unittest.main()
