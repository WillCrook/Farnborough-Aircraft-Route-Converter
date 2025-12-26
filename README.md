# Tasmead Display Tools

A PyQt6 GUI application for:

- **Transpose to Airfield** – Adjust KML files for target airfields with latitude, longitude, heading, and elevation.  
- **Debris Trajectory Simulation** – Calculate debris trajectories from KML data, coordinates, or bearing inputs.

---

## Features

- Drag & drop KML files for processing.  
- Save/load presets for airfields and simulation configurations.  
- Automatic unit conversion between metres and feet.  
- Debris trajectory simulation with configurable physics and surface types.  
- Summary output: heading, air distance, ground distance, total distance, and number of impacts.  
- Export results to KML.

---

## Installation

```bash
git clone https://github.com/WillCrook/Farnborough-Aircraft-Route-Converter.git
cd Farnborough-Aircraft-Route-Converter
python -m venv .venv
source .venv/bin/activate  # Mac/Linux
.venv\Scripts\activate     # Windows
pip install -r requirements.txt
python src/main.py
