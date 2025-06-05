# GF2 Logic Simulator

A Python-based digital logic circuit simulator supporting both command-line and graphical user interfaces. The simulator allows users to define, simulate, and monitor digital circuits using a custom definition file format.

---

## Table of Contents
- [Project Overview](#project-overview)
- [Key Files & Structure](#key-files--structure)
- [How to Run](#how-to-run)
- [Definition File Format](#definition-file-format)
- [Sample Circuits](#sample-circuits)
- [Testing](#testing)
- [License](#license)

---

## Project Overview
This project is a logic simulation program written in Python 3. It covers all major phases of the software engineering life cycle: specification, design, implementation, testing, and maintenance. The simulator can parse user-supplied circuit definition files, build the corresponding logic network, and simulate its behavior. Both command-line and graphical interfaces are provided for user interaction.

---

## Key Files & Structure

- **logsim/logsim.py**: Main entry point. Parses command-line arguments and launches either the CLI or GUI.
- **logsim/devices.py**: Defines logic devices (gates, switches, clocks, etc.) and their properties.
- **logsim/names.py**: Maps variable and string names to unique integer IDs for efficient internal referencing.
- **logsim/network.py**: Manages the connections between devices and executes the logic network.
- **logsim/monitors.py**: Allows users to monitor and record output signals from devices.
- **logsim/parse.py**: Parses and validates the user-supplied circuit definition file, building the network.
- **logsim/scanner.py**: Reads and tokenizes the definition file for the parser.
- **logsim/userint.py**: Implements the interactive command-line interface.
- **logsim/gui.py**: Implements the graphical user interface using wxPython and OpenGL.
- **logsim/test_*.py**: Unit tests for each module, using pytest.
- **logsim/*.txt**: Example and test circuit definition files.

---

## How to Run

### Prerequisites
- Python 3.8+
- wxPython (`pip install wxPython`)
- OpenGL (`pip install PyOpenGL`)

### Command-Line Interface (CLI)
Run a simulation using a definition file:
```sh
python3 logsim/logsim.py -c logsim/full_adder.txt
```

### Graphical User Interface (GUI)
Launch the GUI with a definition file:
```sh
python3 logsim/logsim.py logsim/full_adder.txt
```

Add `-h` for help:
```sh
python3 logsim/logsim.py -h
```

---

## Definition File Format
Definition files describe the digital circuit to be simulated. They support the following sections:
- `DEVICES`: Declare all devices (gates, switches, clocks, etc.)
- `CONNECT`: Specify connections between device outputs and inputs
- `MONITOR`: List outputs to be monitored during simulation
- `END`: Marks the end of the definition

**Example:**
```plaintext
DEVICES X1:XOR, X2:XOR, A1:AND 2, S1:SWITCH 1;
CONNECT S1 > X1.I1, X1 > X2.I1;
MONITOR X2;
END
```

---

## Sample Circuits
- **logsim/full_adder.txt**: Full adder circuit
- **logsim/flip_flop.txt**: D-type flip-flop circuit
- **logsim/test_break.txt, test_break_2.txt**: Example files with syntax errors for testing

---

## Testing
Unit tests are provided for all major modules. To run all tests:
```sh
pytest logsim/
```

---

## License
This project is for educational purposes.
