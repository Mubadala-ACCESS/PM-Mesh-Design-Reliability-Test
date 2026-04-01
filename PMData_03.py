# Record Both PM Data From RPI 

import threading
import csv
import time
from datetime import datetime

import sensors as sens


lock = threading.Lock()
latest_results = {}


def read_pm_sensor(sensor):
    global latest_results

    try:
        data = sensor.measurePM_10_seconds()

        result = {
            "PM1count": data.get("PM1count"),
            "PM2_5count": data.get("PM2,5count"),
            "PM10count": data.get("PM10count"),
            "PM1mass": data.get("PM1mass"),
            "PM2_5mass": data.get("PM2,5mass"),
            "PM10mass": data.get("PM10mass"),
            "sensor_T": data.get("sensor_T"),
            "sensor_RH": data.get("sensor_RH"),
        }

        with lock:
            latest_results[sensor.index] = result

    except Exception as e:
        print(f"Error reading sensor {sensor.index}: {e}")
        with lock:
            latest_results[sensor.index] = {
                "PM1count": None,
                "PM2_5count": None,
                "PM10count": None,
                "PM1mass": None,
                "PM2_5mass": None,
                "PM10mass": None,
                "sensor_T": None,
                "sensor_RH": None,
            }


def build_row(timestamp, sensor1_index, sensor2_index):
    s1 = latest_results.get(sensor1_index, {})
    s2 = latest_results.get(sensor2_index, {})

    return {
        "timestamp": timestamp,

        "sensor1_index": sensor1_index,
        "sensor1_PM1count": s1.get("PM1count"),
        "sensor1_PM2_5count": s1.get("PM2_5count"),
        "sensor1_PM10count": s1.get("PM10count"),
        "sensor1_PM1mass": s1.get("PM1mass"),
        "sensor1_PM2_5mass": s1.get("PM2_5mass"),
        "sensor1_PM10mass": s1.get("PM10mass"),
        "sensor1_sensor_T": s1.get("sensor_T"),
        "sensor1_sensor_RH": s1.get("sensor_RH"),

        "sensor2_index": sensor2_index,
        "sensor2_PM1count": s2.get("PM1count"),
        "sensor2_PM2_5count": s2.get("PM2_5count"),
        "sensor2_PM10count": s2.get("PM10count"),
        "sensor2_PM1mass": s2.get("PM1mass"),
        "sensor2_PM2_5mass": s2.get("PM2_5mass"),
        "sensor2_PM10mass": s2.get("PM10mass"),
        "sensor2_sensor_T": s2.get("sensor_T"),
        "sensor2_sensor_RH": s2.get("sensor_RH"),
    }


def main():
    global latest_results

    filename = "particle_two_sensors_full.csv"

    pm_sensors = [
        s for s in sens.sensors
        if getattr(s, "SENSOR", None) == "particulate_matter"
    ]

    if len(pm_sensors) != 2:
        print(f"Expected 2 particulate sensors, found {len(pm_sensors)}")
        return 1

    pm_sensors = sorted(pm_sensors, key=lambda s: s.index)

    sensor1 = pm_sensors[0]
    sensor2 = pm_sensors[1]

    sensor1_index = sensor1.index
    sensor2_index = sensor2.index

    print("Logging started")
    print(f"Sensor 1 = particulate sensor with index {sensor1_index}")
    print(f"Sensor 2 = particulate sensor with index {sensor2_index}")
    print(f"Saving to {filename}")
    print("Logging interval: 60 seconds")

    fieldnames = [
        "timestamp",

        "sensor1_index",
        "sensor1_PM1count",
        "sensor1_PM2_5count",
        "sensor1_PM10count",
        "sensor1_PM1mass",
        "sensor1_PM2_5mass",
        "sensor1_PM10mass",
        "sensor1_sensor_T",
        "sensor1_sensor_RH",

        "sensor2_index",
        "sensor2_PM1count",
        "sensor2_PM2_5count",
        "sensor2_PM10count",
        "sensor2_PM1mass",
        "sensor2_PM2_5mass",
        "sensor2_PM10mass",
        "sensor2_sensor_T",
        "sensor2_sensor_RH",
    ]

    with open(filename, "a", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if csvfile.tell() == 0:
            writer.writeheader()

        while True:
            cycle_start = time.time()
            timestamp = datetime.now().isoformat()
            latest_results = {}

            t1 = threading.Thread(target=read_pm_sensor, args=(sensor1,))
            t2 = threading.Thread(target=read_pm_sensor, args=(sensor2,))

            t1.start()
            t2.start()

            t1.join()
            t2.join()

            row = build_row(timestamp, sensor1_index, sensor2_index)
            writer.writerow(row)
            csvfile.flush()

            print(
                f"{timestamp} | "
                f"Sensor1(index={sensor1_index}) PM2.5 mass={row['sensor1_PM2_5mass']} | "
                f"Sensor2(index={sensor2_index}) PM2.5 mass={row['sensor2_PM2_5mass']}"
            )

            elapsed = time.time() - cycle_start
            time.sleep(max(0, 60 - elapsed))


if __name__ == "__main__":
    main()
