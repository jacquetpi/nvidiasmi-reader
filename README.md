# Simple nvidia-smi reader 

Easily measure the power consumption of NVIDA graphic cards

## Features

Dump in a CSV file NVIDIA GC indicators (including the power consumption) using $nvidia-smi$ (must be pre-installed)

## Usage

```bash
python3 nvidiasmi-reader.py --help
```

To dump on default ```consumption.csv``` while also displaying measures to the console
```bash
python3 nvidiasmi-reader.py --live
```

To change default values:
```bash
python3 nvidiasmi-reader.py --delay=(sec) --precision=(number of digits) --output=consumption.csv
```
