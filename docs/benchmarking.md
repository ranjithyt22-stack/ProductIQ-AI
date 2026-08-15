# Industrial Benchmark Dataset Specification (v1.0)

## 1. Overview
The Industrial Benchmark dataset (`data/benchmark/`) provides an independently defined gold standard across 10 diverse industrial commerce product categories.

---

## 2. Benchmark Categories & Products

| ID | Product Name | Category | Manufacturer | Total Ground Truth Specs |
|---|---|---|---|---|
| `BENCH-001` | Industrial Pneumatic Cylinder PC-50-100 | Pneumatic Cylinder | Acme Industrial Systems | 7 |
| `BENCH-002` | High-Flow Directional Solenoid Valve PV-200 | Solenoid Valve | FlowControl Tech Inc | 6 |
| `BENCH-003` | PT100 Industrial RTD Temperature Sensor | Temperature Sensor | ThermoSense Solutions | 6 |
| `BENCH-004` | Deep Groove Precision Ball Bearing BB-6205-ZZ | Industrial Bearing | Apex Bearings Ltd | 6 |
| `BENCH-005` | Three-Phase Industrial AC Motor EM-3PH-7.5KW | Electric Motor | PowerDrive Electric Co | 6 |
| `BENCH-006` | Axial Piston Variable Hydraulic Pump HP-A10V-45 | Hydraulic Pump | HydroForce Dynamics | 5 |
| `BENCH-007` | Piezoresistive Pressure Transmitter PT-420-16BAR | Pressure Sensor | Sensotech Instruments | 5 |
| `BENCH-008` | Helical Bevel Speed Reducer Gearbox GB-HB-85 | Industrial Gearbox | GearTech PowerDrive | 5 |
| `BENCH-009` | High-Pressure Pilot Solenoid Valve SV-HP-50 | Solenoid Valve | Vortex Fluidics | 5 |
| `BENCH-010` | Precision Electric Linear Actuator LA-12V-300MM | Linear Actuator | LinearMotion Dynamics | 6 |

---

## 3. Machine-Readable Schema Structure
Each benchmark definition file in `data/benchmark/ground_truth/` contains:
- `product_id`: Unique identifier (e.g. `BENCH-001`).
- `product_name`, `manufacturer`, `product_code`, `category`, `description`.
- `specifications`: Array of `{ name, value, unit, raw_value, page, verbatim_evidence }`.
- `negative_test_attributes`: List of attributes intentionally omitted from source text for hallucination testing.
- `expected_readiness`: Canonical expected readiness status (`READY_FOR_COMMERCE`, `REVIEW_REQUIRED`, `NOT_READY`).
