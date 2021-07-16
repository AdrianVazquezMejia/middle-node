'''
Created on Jul 9, 2021

@author: adrian
'''
import unittest

import sqlite3
# from sqlite_manager import load_json
from src.sqlite_manager import *


class TestLoadJson(unittest.TestCase):
    def setUp(self):

        conn = sqlite3.connect("meter_db.sqlite")
        cur = conn.cursor()
        cur.execute('DROP TABLE IF EXISTS meter_table')
        cur.execute(
            'CREATE TABLE meter_table (meter_id TEXT, energy INTEGER,date TEXT, status BOOLEAN)'
        )
        cur.execute(
            'INSERT INTO meter_table (meter_id, energy,date, status) VALUES (?, ?, ?, ? )',
            ("00fe00", 0, "2021-06-26 18:41:23.580757", True))
        cur.execute(
            'INSERT INTO meter_table (meter_id, energy,date, status) VALUES (?, ?, ?, ? )',
            ("00ff01", 0, "2021-06-26 18:41:23.580757", True))
        cur.execute(
            'INSERT INTO meter_table (meter_id, energy,date, status) VALUES (?, ?, ?, ? )',
            ("00ff02", 0, "2021-06-26 18:41:23.580757", True))
        cur.execute(
            'INSERT INTO meter_table (meter_id, energy,date, status) VALUES (?, ?, ?, ? )',
            ("00ff03", 0, "2021-06-26 18:41:23.580757", True))
        cur.execute(
            'INSERT INTO meter_table (meter_id, energy,date, status) VALUES (?, ?, ?, ? )',
            ("00ff04", 0, "2021-06-26 18:41:23.580757", True))
        conn.commit()
        cur.close()

    def testIDisOnJson(self):

        expected_id = "0001"
        actual_output = load_json(id="0001", write_api_key="PYF7YMZNOM3TJVSM")
        actual_id = actual_output["id"]
        self.assertEqual(actual_id, expected_id, "Must have the same id")

    def testAPIKeyOnJson(self):

        expected_write_api_key = "PYF7YMZNOM3TJVSM"
        actual_output = load_json(id="0001", write_api_key="PYF7YMZNOM3TJVSM")
        actual_write_api_key = actual_output["write_api_key"]
        self.assertEqual(actual_write_api_key, expected_write_api_key,
                         "Must have the same api key")

    def testLenOfDic(self):

        actual_output = load_json(id="0001", write_api_key="PYF7YMZNOM3TJVSM")
        actual_len = len(actual_output)
        self.assertEqual(actual_len, 3, "Must have 3 fields")

    def testIsUpdatesOnOutput(self):

        actual_output = load_json(id="0001", write_api_key="PYF7YMZNOM3TJVSM")
        isUpdatesOnOutput = "updates" in actual_output
        self.assertTrue(isUpdatesOnOutput, "Must contain updates")

    def testFieldOfUpdates(self):

        actual_output = load_json(id="0001", write_api_key="PYF7YMZNOM3TJVSM")

        for meter_card in actual_output["updates"]:
            self.assertTrue("meterid" in meter_card,
                            "Must contain a meterid key")
            self.assertTrue("energy" in meter_card, "Must contain energy key")
            self.assertTrue("date" in meter_card, "Must contain energy key")
            self.assertTrue("state" in meter_card, "Must contain energy key")


if __name__ == "__main__":
    unittest.main()
