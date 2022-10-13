## General
#

# Electromagnetics
e0 = 1.602176634e-19        # [C]

eps0 = 8.8541878128e-12     # [F/m]
mu0 = 1.25663706212e-6      # [N/A²]

c = 299792458               # [m/s]

# Thermal
kB = 1.380649e-23   # [J/K]

T0C = 273.15        # [K]


## Materials
#

# Silicon
class Si:
    eps = 11.7*eps0
