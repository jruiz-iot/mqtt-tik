import paho.mqtt.client as mqtt

# This is the Publisher
def publish(measurement, value):
    client = mqtt.Client()
    client.connect("localhost",1883,60)
    client.publish("air_sensor", "%s,site=office value=%s" % (measurement, value))
    client.disconnect()

