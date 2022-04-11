# Sensor TCT Setup at ETHZ (Rubbia-Group)

## Requirements
- This framework is only implemented to be used with Linux
  - Especially the Particulars laser control and Standa stage control will not work on other platforms

## Dependencies

### libxmic-2.13.3
For controlling the X-Y-Z stage from Standa, the ximc library is used.

Under Linux (Debian-like or Red-hat-like) the library can easily be installed via `dpkg -i ...` using the corresponding `.deb`packages or `rpm -i ...` using the `.rpm` packages.
The following two packages need to be installed:

- **libximc7_2.13.3-1**
- **libximc7-dev_2.13.3-1** / **libximc7-devel-2.13.3-1**

Please download the library from: [https://files.xisupport.com/libximc/libximc-2.13.3-all.tar.gz](https://files.xisupport.com/libximc/libximc-2.13.3-all.tar.gz).
The `.dep` and `.rpm` files can be found within this archive under `ximc-2.13.3/ximc/dep` resp. `ximc-2.13.3/ximc/rep`.

For ease of use, the corresponding Python wrapper, which can be found under `ximc-2.13.3/ximc/crossplatform/wrappers/python/pyximc.py` is provided as part of this framework under `tct/lab/Standa/pyximc.py`. The file provided here is copied 1:1 from the libximc release.

Given that the exact binding of the Python wrapper with the library is not know, **the requirement for libximc 2.13.3 is strict**.

#### UDEV Rules
Installing the libximc via

### Python3.7 or higher
This framework only works with python 3.7 or higher.

- This is notably for the requirement of `dict` being insertion ordered (see: https://stackoverflow.com/a/39980744)

#### Python3 Packages
- python-vxi11
- scipy
- numpy
- matplotlib
- plotly
- pyserial
