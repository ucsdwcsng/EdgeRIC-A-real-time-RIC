import random
import time
from influxdb import InfluxDBClient

# Setup InfluxDB connection
client = InfluxDBClient('localhost', 8086, 'root', 'root', 'environmental_data')

def generate_data():
    """Generate random data points for temperature, humidity, and pressure."""
    temperature = random.uniform(20.0, 30.0)  # Simulate temperature in Celsius
    humidity = random.uniform(40.0, 60.0)  # Simulate humidity in %
    pressure = random.uniform(980, 1050)  # Simulate pressure in hPa
    return temperature, humidity, pressure

def send_data():
    temperature, humidity, pressure = generate_data()
    json_body = [
        {
            "measurement": "environmental_metrics",
            "tags": {
                "sensor": "sensor1"
            },
            "fields": {
                "temperature": temperature,
                "humidity": humidity,
                "pressure": pressure
            }
        }
    ]
    client.write_points(json_body)

if __name__ == '__main__':
    while True:
        send_data()
        time.sleep(2)  # Send data every 2 seconds
