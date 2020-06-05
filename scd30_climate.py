import sys
import os
import requests
sys.path.insert(0, "..")

#SDC30 Sensor
import smbus
import RPi.GPIO as gpio
import struct
from db_connection import write_points
#MySQL
#import MySQLdb
import time

#MySQL
#db = MySQLdb.connect("212.227.201.63", "FarmData", "Mc11xi!2", "fc_Documentation")
# Hana Express
#hana_url = 'http://hxehost:4000/write-sensor-data'

#SDC30
bus = smbus.SMBus(1)
sdc30_addr = 0x61

co2_raw = [0, 0, 0, 0]
temp_raw = [0, 0, 0, 0]
humi_raw = [0, 0, 0, 0]

#co2_min_limit = 800

#def co2_valve_trig(on_sec):
#    os.system('sudo sispmctl -o 1')
#    time.sleep(on_sec)
#    os.system('sudo sispmctl -f 1')
#    status = os.system('sudo sispmctl -nqg 1')
#    return status

if __name__ == "__main__":
    try:
        #curs = db.cursor()

        # Node objects have methods to read and write node attributes as well as browse or populate address space

        #Read Ready-Status
        bus.write_i2c_block_data(sdc30_addr, 0x02, [0x02])
        time.sleep(4)
        ready = bus.read_i2c_block_data(sdc30_addr, 0x00)
        print(ready)
        time.sleep(1)

        #Write CMD to Measurement/Reading from Sensor
        bus.write_i2c_block_data(sdc30_addr, 0x03, [0x00])
        time.sleep(4)
        test = bus.read_i2c_block_data(sdc30_addr, 0x00)
        time.sleep(.5)

        #Read Values from SDC30
        if ready:
            raw_val = bus.read_i2c_block_data(sdc30_addr, 0x00)
            time.sleep(.5)
        else:
            print("No Data for Output")
        time.sleep(2)

        #CO2 Value: List -> bytearray -> Big endian notation -> 32bit Float
        co2_raw[0] = raw_val[0]
        co2_raw[1] = raw_val[1]
        co2_raw[2] = raw_val[3]
        co2_raw[3] = raw_val[4]
        co2_val = bytearray(co2_raw)
        co2 = struct.unpack('>f', co2_val)[0]
        print("CO2 = %f" % co2)
        time.sleep(.5)

        #Temperature Value: List -> bytearray -> Big endian notation -> 32bit Float
        temp_raw[0] = raw_val[6]
        temp_raw[1] = raw_val[7]
        temp_raw[2] = raw_val[9]
        temp_raw[3] = raw_val[10]
        temp_val = bytearray(temp_raw)
        temp = struct.unpack('>f', temp_val)[0]
        print("Temperature = %f" % temp)
        time.sleep(.5)

        #Humidity Value: List -> bytearray -> Big endian notation -> 32bit Float
        humi_raw[0] = raw_val[12]
        humi_raw[1] = raw_val[13]
        humi_raw[2] = raw_val[15]
        humi_raw[3] = raw_val[16]
        humi_val = bytearray(humi_raw)
        humi = struct.unpack('>f', humi_val)[0]
        print("Humidity = %f" % humi)
        time.sleep(.5)

        #Get Local Time
        #timestamp=time.strftime('%Y-%m-%d %H:%M:%S')
        #hour = time.localtime(time.time())

        #curs.execute ("INSERT INTO farmData (time,value,valueType,sensorID) VALUES (%s,%s,%s,%s)", (timestamp, temp, 0, 47,))
        #curs.execute ("INSERT INTO farmData (time,value,valueType,sensorID) VALUES (%s,%s,%s,%s)", (timestamp, humi, 1, 47,))
        #curs.execute ("INSERT INTO farmData (time,value,valueType,sensorID) VALUES (%s,%s,%s,%s)", (timestamp, co2, 4, 47,))

        #if (co2 < co2_min_limit and hour.tm_hour >= 6 and hour.tm_hour <=21): #active CO2 supply from 8 am till 12 am
        #    socket2_state = co2_valve_trig(10)
            #print("Socket 2 = ", socket2_state)
        #    curs.execute ("INSERT INTO farmData (time,value,valueType,sensorID) VALUES (%s,%s,%s,%s)", (timestamp, 1, 7, 41,))
        #else:
        #	curs.execute ("INSERT INTO farmData (time,value,valueType,sensorID) VALUES (%s,%s,%s,%s)", (timestamp, 0, 7, 41,))

        #curs.close()
        #db.commit()
        #temp_json = {"sensor_id": 4, "value": temp}
        #humi_json = {"sensor_id": 5, "value": humi}
        #co2_json = {"sensor_id": 6, "value": co2}
        #r = requests.post(url = hana_url, json= temp_json)
        #h = requests.post(url = hana_url, json= humi_json)
        #c = requests.post(url = hana_url, json= co2_json)
        #print(r.text, h.text, c.text)
        #co2, temperature, humidity = [struct.unpack('>f', bytes(data[i:i + 4]))[0] for i in range(0, len(data), 4)]
        # prepare payload for database
        data_write = {
            'temperature': temp,
            'humidity': humi,
            'co2': co2,
        }
        if temp > 0:
            write_points(chamber='habitacion', metric='co2_t_h', **data_write)
            print('CO2: ', co2, 'Temperature: ', temp, 'Humidity: ', humi)
        else:
            print('Not available')
            pass
    finally:
        pass
