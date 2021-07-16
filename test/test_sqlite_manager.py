'''
Created on Jul 7, 2021

@author: adrian
'''
import unittest
import sqlite3

# from sqlite_manager import energy_load
from src.sqlite_manager import *

# loras = [{"loraid":255,"slaves":[1,2,3]},{"loraid":254,"slaves":[0]}]   Original
loras = [{"loraid":255, "slaves":[1, 2, 3, 4]}, {"loraid":254, "slaves":[0]}]  # Para el test


class Test(unittest.TestCase): 

    def testSerialMetersCreates(self):
        # SR01 #SR05 #SR09

        conn = sqlite3.connect('meter_db.sqlite')
        cur = conn.cursor()
        cur.execute('DROP TABLE IF EXISTS meter_table')
        energy_load(loras)
        cur.execute('SELECT meter_id FROM meter_table ORDER BY meter_id ASC')
        expected_meter_id = ["00fe00", "00ff01", "00ff02", "00ff03", "00ff04"]
        actual_meter_id = []
        for row in cur:
            actual_meter_id.append(row[0])
        cur.close()
        self.assertEqual(actual_meter_id, expected_meter_id, "Must be equal")

    def testDataBaseCreation(self):
        # SR21 #SR06

        conn = sqlite3.connect('meter_db.sqlite')
        cur = conn.cursor()
        cur.execute('DROP TABLE IF EXISTS meter_table')
        energy_load(loras)
        cur.execute('SELECT name FROM sqlite_master WHERE type= ? AND name= ? ', ('table', 'meter_table'))
        expected_relation_name = "meter_table"
        actual_relation_name = cur.fetchone()[0]
        cur.close()
        self.assertEqual(expected_relation_name, actual_relation_name, "Table does not exists")

    def testNewMeterAdd(self):
        # SR07 #SR09

        conn = sqlite3.connect("meter_db.sqlite") 
        cur = conn.cursor()
        cur.execute('DROP TABLE IF EXISTS meter_table')

        energy_load(loras)
        cur.execute('SELECT * FROM meter_table WHERE meter_id = ?', ("00fe00",))
        actual_tuple = cur.fetchone()
        expected_id = "00fe00"
        expected_energy = 0
        expected_state = 1
        actual_id = actual_tuple[0]
        actual_energy = actual_tuple[1]
        actual_state = actual_tuple[3]
        cur.close()
        self.assertEqual(actual_id, expected_id)
        self.assertEqual(actual_energy, expected_energy)
        self.assertEqual(actual_state, expected_state)

    def testNoAddExistingMeter(self):
        # SR08

        conn = sqlite3.connect("meter_db.sqlite")
        cur = conn.cursor()
        cur.execute('DROP TABLE IF EXISTS meter_table')
        cur.execute('CREATE TABLE meter_table (meter_id TEXT, energy INTEGER, date TEXT, status BOOLEAN)')
        cur.execute('INSERT INTO meter_table (meter_id, energy,date,status) VALUES (?, ?, ?,?)', ("00fe00", 0, "00:00", True))
        conn.commit()
        cur.close()
        energy_load(loras)
        cur = conn.cursor()
        cur.execute('SELECT * FROM meter_table WHERE meter_id = ?', ("00fe00",))
        expected_len = len(cur.fetchall())
        self.assertEqual(1, expected_len)
        cur.close()
   
        
if __name__ == "__main__":
    import sys
    sys.argv = ['', 'Test.testName']
    unittest.main()
