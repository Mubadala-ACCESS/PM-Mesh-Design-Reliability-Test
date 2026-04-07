# PM Sensor Mesh Enclosure Validation

## Overview

This project documents the design, implementation, and validation of a **mesh-based inlet enclosure** for particulate matter (PM) sensors used in a portable weather station.

The goal is to protect the sensor from:

* Direct rainfall
* Insects and debris
* Harsh environmental exposure

while ensuring that the **measurement performance is not affected**.

---

## Problem Statement

During field deployment, the PM sensors experienced failures due to:

* Water ingress during rain events
* Contamination from environmental particles and insects

These issues resulted in **sensor degradation and unreliable readings**.

---

## Proposed Solution

A **mesh-based inlet enclosure** was designed to:

* Prevent direct rain entry
* Block insects and large particles
* Maintain sufficient airflow for accurate PM measurements

---

## System Components

### Sensors

* Next PM Tera Sensor (x2)

### Reference Instrument

* Fidas 200 (for validation and calibration comparison)

### Weather Station Setup

* Outdoor deployment under real environmental conditions

---

## Experimental Design

### Objective

To evaluate whether the mesh enclosure affects sensor performance.

### Methodology

A **24-hour comparative experiment** was conducted:

| Sensor   | Configuration          |
| -------- | ---------------------- |
| Sensor A | Without mesh enclosure |
| Sensor B | With mesh enclosure    |

Both sensors were:

* Operated simultaneously
* Exposed to identical environmental conditions
* Compared against Fidas 200 reference data

---

## Experimental Setup Diagram

```
        ┌───────────────────────────────┐
        │        Weather Station        │
        │                               │
        │   ┌───────────────┐           │
        │   │  Sensor A     │           │
        │   │ (No Mesh)     │           │
        │   └───────────────┘           │
        │                               │
        │   ┌───────────────┐           │
        │   │  Sensor B     │           │
        │   │ (With Mesh)   │           │
        │   └───────────────┘           │
        │                               │
        └────────────┬──────────────────┘
                     │
                     │ Data Comparison
                     ▼
             ┌───────────────┐
             │   Fidas 200   │
             │  Reference    │
             └───────────────┘
```

---

## Mesh Enclosure Design

### Key Features

* Fine mesh layer to block water droplets
* Air-permeable structure
* Durable material suitable for outdoor conditions

### Concept Diagram

```
        Airflow
          ↓
    ┌───────────────┐
    │   Mesh Layer  │  ← Rain / Insect Barrier
    ├───────────────┤
    │  Air Chamber  │
    ├───────────────┤
    │   PM Sensor   │
    └───────────────┘
```

---

## Data Collection

### Duration

* 24 hours continuous monitoring

### Parameters

* PM2.5 / PM10 readings (from sensors)
* Reference readings (Fidas 200)
* Environmental conditions (rain, humidity, wind)

---

## Results

### Observations

* Sensor with mesh enclosure remained protected from water exposure
* No physical contamination observed inside the enclosure

### Performance Comparison

| Metric                     | Without Mesh | With Mesh |
| -------------------------- | ------------ | --------- |
| Data Stability             | TBD          | TBD       |
| Correlation with Fidas 200 | TBD          | TBD       |
| Signal Deviation           | TBD          | TBD       |

---

## Analysis

* Compare time-series data between both sensors
* Calculate correlation coefficient with Fidas 200
* Identify any delay or damping effect caused by mesh

---

## Conclusion

The mesh enclosure is expected to:

* Improve durability and reliability of the PM sensor
* Prevent environmental damage
* Maintain acceptable measurement accuracy

Final validation depends on quantitative analysis of collected data.

---

## Future Work

* Optimize mesh density and material
* Long-term testing under extreme weather conditions
* Integration into production design

---

## Repository Structure

```
├── README.md
├── docs/
│   ├── experiment_setup.md
│   ├── results_analysis.md
│   └── diagrams/
├── data/
│   ├── raw/
│   └── processed/
├── scripts/
│   └── analysis.py
└── images/
```

## Author
Muhammed Nabeel
* Researcher working on IoT-based portable weather stations and sensor validation

---

## License

MIT License
