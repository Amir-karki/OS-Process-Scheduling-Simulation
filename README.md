# Process Scheduling Simulator

A comprehensive simulation tool for exploring and analyzing different CPU scheduling algorithms used in operating systems.

## Overview

This project implements several CPU scheduling algorithms to help understand their behavior, efficiency, and performance characteristics. It provides detailed metrics and visualizations to compare different scheduling approaches.

## Features

- **Multiple Scheduling Algorithms**:
  - First-Come, First-Served (FCFS)
  - Shortest Job First (SJF)
  - Shortest Remaining Time First (SRTF)
  - Round Robin (RR) with configurable time quantum
  - Priority Scheduling (preemptive and non-preemptive)
  - Multilevel Queue Scheduling

- **Process Management**:
  - Process states (New, Ready, Running, Waiting, Terminated)
  - Process attributes (arrival time, burst time, priority)
  - Process tracking (waiting time, turnaround time, response time)

- **Simulation Features**:
  - Time-driven simulation
  - Context switch overhead modeling
  - Customizable process sets

- **Performance Metrics**:
  - Average waiting time
  - Average turnaround time
  - Average response time
  - CPU utilization
  - Throughput

- **Visualization**:
  - Gantt charts for process execution
  - Timeline visualization
  - Metrics comparison charts

- **Data Management**:
  - Process import/export via JSON
  - Detailed results in CSV format
  - Figures saved as PNG files


## Usage

### Basic Usage

```bash
# Run all algorithms with 5 random processes
python src/main.py

# Run with a specific algorithm
python src/main.py --algorithm fcfs

# Run with a specific process file
python src/main.py --file data/sample_processes.json

# Run Round Robin with a custom time quantum
python src/main.py --algorithm rr --quantum 2
```

### Command Line Arguments

- `--processes N`: Generate N random processes (default: 5)
- `--file PATH`: Load processes from a JSON file
- `--seed N`: Set random seed for reproducibility
- `--algorithm ALG`: Choose a specific algorithm (fcfs, sjf, srtf, rr, priority, multilevel, all)
- `--quantum N`: Set time quantum for Round Robin scheduler (default: 4)
- `--no-visualize`: Disable visualization
- `--no-save`: Disable saving results

### Example Output

The simulation produces:
1. Metrics tables showing comparative performance
2. Gantt charts showing process execution timeline
3. Process timeline visualizations
4. CSV files with detailed metrics

## Requirements

- Python 3.7+
- pandas
- matplotlib
- numpy

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/process-scheduler.git
cd process-scheduler

# Create a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## License

MIT License

## Authors
- Amir Karki
- Sanskar Bajimaya
