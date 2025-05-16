

# RTLola-FMU Evaluation Scripts

This repository provides a collection of Python scripts for testing and analyzing Functional Mock-up Units (FMUs) with RTLola runtime integration. Monitoring FMUs properties up to a user defined specifications. The tools support benchmarking, visual analysis, and specification switching during simulation.

## Contents

### 1. `benchmark_fmu.py`

Benchmarks FMU performance with and without RTLola integration. Measures:

* Average step execution time
* Total simulation duration
* Memory usage (RSS)

#### Usage

Edit the script to specify the FMU paths:

```python
regular_fmu = "fmus/BouncingBall.fmu"
rtlola_fmu = "fmus_RTLola_FFI/BouncingBall.fmu"
```

Then run the script:

```bash
python benchmark_fmu.py
```

#### Output

Displays a table comparing baseline and RTLola-instrumented FMU performance, along with percentage overhead.

---

### 2. `visualize_triggers.py`

Runs an FMU simulation and generates a plot of variable outputs over time, highlighting points where RTLola triggers are activated.

#### Features

* Interactive visualization using Plotly
* Trigger points marked with visual indicators
* Example use of dynamic input response based on trigger conditions


#### Usage

Ensure the FMU path is correct inside the script, then execute:

```bash
python visualize_triggers.py
```

A browser window will open displaying the plot.

---

### 3. `spec_switch_test.py`

Demonstrates runtime switching of RTLola specifications in response to trigger events during simulation.

#### Features

* Monitors RTLola output for specific triggers
* Dynamically replaces the active `.lola` specification via `rtlola_spec` input
* Tests the FMU's ability to adapt its monitoring logic at runtime

#### Usage

No command-line arguments needed. Just run the script:

```bash
python spec_switch_test.py
```

Ensure the required `.lola` specification files are available in the `specifications/` directory.

---

## FMU and File Structure

Expected directory layout:

```
fmus/
├── BouncingBall.fmu               # Baseline FMU without RTLola

fmus_RTLola_FFI/
├── BouncingBall.fmu               # FMU compiled with RTLola via FFI

specifications/
├── bouncing_ball_spec.lola        # Default specification
├── new_ball_spec.lola             # Alternative specification (for switching)
```
---

## Logging

FMI and RTLola log messages can be enabled when instantiating an `FMU3Slave` by passing a custom log handler:

```python
fmu = FMU3Slave(
    guid=model_description.guid,
    unzipDirectory=unzip_dir,
    modelIdentifier=model_description.coSimulation.modelIdentifier,
    instanceName="instance1",
)

fmu.instantiate(
    loggingOn=True,                  # Enable FMI logging
    logMessage=custom_logger         # Custom Python log handler
)
```

## Requirements

Install dependencies with:

```bash
pip install fmpy plotly psutil pandas numpy
```

Python 3.7 or later is recommended.

---

## Notes

* All FMUs must comply with the FMI 3.0 standard and support Co-Simulation.
* The `rtlola_spec` and `rtlola_output` variables must be defined within the FMUs.
* Logging output is saved to `fmu_simulation.log`.



