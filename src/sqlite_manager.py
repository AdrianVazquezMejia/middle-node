"""! @brief Insert, actualize and post data in a database."""

# #
# @file sqlite_manager.py
#
# @brief SQL management for energy storage on disk

# @section author_sqlite_manager Author(s)
# - Created by Adrian Vazquez on 07/01/2021.
# - Modified by Daniel Malaver on 07/13/2021.
#
# Copyright (c) 2021 Corporacion Estelio.  All rights reserved.

import sqlite3
import datetime
import json


def energy_load(loras):
    """! Organize meters' characteristics in a database with 
        the meter ID in hexadecimal way, 
        the energy, the date of creation and the status 

    @param loras   Array of dictionaries with meters'characteristics
    """
    data_base_connection = sqlite3.connect("meter_db.sqlite")
    data_base_cursor = data_base_connection.cursor()
    data_base_cursor.execute(
        "CREATE TABLE IF NOT EXISTS meter_table (meter_id TEXT,energy INTEGER,date TEXT, status BOOLEAM)"
    )
    data_base_connection.commit()
    for lora in loras:

        lora_id_to_byte = (lora["loraid"]).to_bytes(2, "big")
        for slave in lora["slaves"]:
            slave_number_to_byte = (slave).to_bytes(1, "big")
            meter_id = lora_id_to_byte + slave_number_to_byte
            data_base_cursor.execute(
                "SELECT * FROM meter_table WHERE meter_id = ?",
                (meter_id.hex(), ))
            if data_base_cursor.fetchone() is None:
                date = datetime.datetime.now()
                data_base_cursor.execute(
                    "INSERT INTO meter_table(meter_id,energy,date,status) VALUES(?,?,?,?)",
                    (meter_id.hex(), 0, date, 1))
            data_base_connection.commit()
    data_base_cursor.close()


def load_json(id, write_api_key):
    """! Post a dictionary with meters' characteristics
     located in the database

    @param id              dictionary ID  
    @param write_api_key   identifier key

    @return dic_meters     dictionary with database's information
    """
    data_base_connection = sqlite3.connect("meter_db.sqlite")
    data_base_cursor = data_base_connection.cursor()
    dic_meters = {
        "id": id,
        "write_api_key": write_api_key,
    }
    dic_meters["updates"] = []
    data_base_cursor.execute("SELECT * FROM meter_table")
    for row in data_base_cursor:
        dic_meters["updates"].append({
            "meterid": row[0],
            "energy": row[1],
            "date": row[2],
            "state": row[3]
        })
    data_base_cursor.close()
    return dic_meters


def update_date_base(meterid, data):
    """! Actualize information in the database

    @param meterid   meter's ID 
    @param data      value to set energy in the database

    @return success or error code    
    """
    time = datetime.datetime.now()
    data_base_connection = sqlite3.connect("meter_db.sqlite")
    data_base_cursor = data_base_connection.cursor()
    data_base_cursor.execute(
        "SELECT meter_id FROM meter_table WHERE meter_id = ?", (meterid, ))
    is_in_database = data_base_cursor.fetchall()
    result = -1
    if is_in_database:
        data_base_cursor.execute(
            "UPDATE meter_table SET energy = ?, date = ? WHERE meter_id = ?", (
                data,
                time,
                meterid,
            ))
        data_base_connection.commit()
        result = 0
    data_base_cursor.close()
    return result


if __name__ == '__main__':
    """! Main program entry
    """
    print("Hello world")
    loras = [{
        "loraid": 255,
        "slaves": [1, 2, 3, 4]
    }, {
        "loraid": 254,
        "slaves": [0]
    }]
    energy_load(loras)
    return_json = load_json(id="0001", write_api_key="PYF7YMZNOM3TJVSM")
    for meter_serial in return_json["updates"]:
        data_test_main = 3210
        return_update_date_base = update_date_base(meter_serial["meterid"],
                                                   data_test_main)
        print("Success") if return_update_date_base == 0 else print("Error")
