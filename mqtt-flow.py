import machine
import time
import network
from umqtt.simple import MQTTClient

# Constants
FLOW_PIN = 5  # Pin connected to the water flow sensor
CALIBRATION_FACTOR = 7.5  # Calibration factor for your sensor (adjust as necessary)
WIFI_SSID = 'your_wifi_ssid'
WIFI_PASSWORD = 'your_wifi_password'
MQTT_BROKER = 'your_mqtt_broker_ip'
MQTT_TOPIC = 'water/flowrate'

# Flow sensor
flow_sensor = machine.Pin(FLOW_PIN, machine.Pin.IN, machine.Pin.PULL_UP)
flow_pulse_count = 0

# WiFi setup
def connect_wifi():
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    wifi.connect(WIFI_SSID, WIFI_PASSWORD)
    
    while not wifi.isconnected():
        time.sleep(1)
    print('Connected to WiFi')
    print(wifi.ifconfig())

# Interrupt handler for flow sensor pulses
def count_flow_pulse(pin):
    global flow_pulse_count
    flow_pulse_count += 1

# Attach the interrupt to the flow sensor pin
flow_sensor.irq(trigger=machine.Pin.IRQ_RISING, handler=count_flow_pulse)

# MQTT setup
def connect_mqtt():
    client = MQTTClient('ESP32', MQTT_BROKER)
    client.connect()
    print('Connected to MQTT Broker')
    return client

# Main function to calculate flow rate and publish to MQTT
def main():
    connect_wifi()
    client = connect_mqtt()
    
    global flow_pulse_count
    while True:
        # Get the pulse count for the last second
        pulse_count = flow_pulse_count
        flow_pulse_count = 0  # Reset the pulse count
        
        # Calculate flow rate (Liters per minute)
        flow_rate = pulse_count / CALIBRATION_FACTOR
        
        # Publish flow rate to MQTT broker
        print("Flow rate: {:.2f} L/min".format(flow_rate))
        client.publish(MQTT_TOPIC, str(flow_rate))
        
        # Wait 1 second before the next reading
        time.sleep(1)

# Run the main loop
main()
