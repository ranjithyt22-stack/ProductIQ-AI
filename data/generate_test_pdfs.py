"""
Script to generate test PDF datasheets for testing arbitrary PDF upload workflow.
"""

import os
import pymupdf as fitz

DATA_DIR = "data"


def generate_temp_sensor_pdf(output_path: str):
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)
    content = """DEMO INDUSTRIAL TECHNOLOGIES
TECHNICAL DATASHEET - INDUSTRIAL TEMPERATURE SENSOR

Product Name: Industrial Temperature Sensor TS-200
Manufacturer: Demo Industrial Technologies
Product Code: TS-200
Category: Temperature Sensor
Description: High precision industrial temperature sensor probe for process control and machinery monitoring.

TECHNICAL SPECIFICATIONS:
- Temperature Range: -20 to 120 °C
- Accuracy: ±0.5 °C
- Supply Voltage: 24 V
- Probe Length: 150 mm

RECOMMENDED APPLICATIONS: Industrial process monitoring, Machine control systems, HVAC monitoring.
SYNTHETIC DEMO DATA
"""
    page.insert_text(fitz.Point(40, 50), content, fontsize=11)
    doc.save(output_path)
    doc.close()


def generate_pressure_valve_pdf(output_path: str):
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)
    content = """DEMO VALVE SYSTEMS
TECHNICAL DATASHEET - INDUSTRIAL PRESSURE VALVE

Product Name: Industrial Pressure Valve PV-300
Manufacturer: Demo Valve Systems
Product Code: PV-300
Category: Pressure Valve
Description: Heavy duty directional pressure valve for industrial fluid control.

TECHNICAL SPECIFICATIONS:
- Pressure Range: 0 to 16 bar
- Port Size: G1/2
- Body Material: Stainless Steel
- Operating Temperature: -10 to 80 °C

RECOMMENDED APPLICATIONS: Hydraulic power systems, Industrial fluid lines, Chemical processing.
SYNTHETIC DEMO DATA
"""
    page.insert_text(fitz.Point(40, 50), content, fontsize=11)
    doc.save(output_path)
    doc.close()


def generate_bearing_pdf(output_path: str):
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)
    content = """DEMO BEARING WORKS
TECHNICAL DATASHEET - INDUSTRIAL DEEP GROOVE BALL BEARING

Product Name: Industrial Deep Groove Ball Bearing BR-6205
Manufacturer: Demo Bearing Works
Product Code: BR-6205
Category: Ball Bearing
Description: Premium precision deep groove ball bearing for heavy machinery rotation.

TECHNICAL SPECIFICATIONS:
- Bore Diameter: 25 mm
- Outer Diameter: 52 mm
- Width: 15 mm
- Dynamic Load Rating: 14.0 kN

RECOMMENDED APPLICATIONS: Electric motors, Conveyor pulleys, Gearboxes, Industrial machinery.
SYNTHETIC DEMO DATA
"""
    page.insert_text(fitz.Point(40, 50), content, fontsize=11)
    doc.save(output_path)
    doc.close()


if __name__ == "__main__":
    os.makedirs(DATA_DIR, exist_ok=True)
    generate_temp_sensor_pdf(os.path.join(DATA_DIR, "Test_Temperature_Sensor.pdf"))
    generate_pressure_valve_pdf(os.path.join(DATA_DIR, "Test_Pressure_Valve.pdf"))
    generate_bearing_pdf(os.path.join(DATA_DIR, "Test_Industrial_Bearing.pdf"))
    print("All synthetic test PDFs generated cleanly!")
