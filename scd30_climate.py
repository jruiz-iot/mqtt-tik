import sys
import os
import requests
sys.path.insert(0, "..")

#SDC30 Sensor
import smbus
import RPi.GPIO as gpio
import struct
import time
from mqtt.mqtt_functionality import publish


#SDC30
bus = smbus.SMBus(1)
sdc30_addr = 0x61

co2_raw = [0, 0, 0, 0]
temp_raw = [0, 0, 0, 0]
humi_raw = [0, 0, 0, 0]

if __name__ == "__main__":
    try:
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
        co2 = co2*1000
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

        data_write = {
            'status': 'ON',
            'temperature': temp,
            'humidity': humi,
            'co2': co2,
        }
        if temp > 0:
            for k,v in data_write.items():
                publish(k,v)
            
        else:
            print('Not available')
            publish('status', 'Offline')
            pass
    finally:
        pass
