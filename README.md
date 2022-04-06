# Sensor TCT Setup at ETHZ (Rubbia-Group)

## Requirements
- This framework is only implemented to be used with Linux
  - Especially the Particulars laser control and Standa stage control will not work on other platforms

## Dependencies

### Python3.7 or higher
This framework only works with python 3.7 or higher.

- This is notably for the requirement of `dict` being insertion ordered (see: https://stackoverflow.com/a/39980744)

### Python3 Packages
- python-vxi11
- scipy
- numpy
- matplotlib
- plotly
- pyserial
