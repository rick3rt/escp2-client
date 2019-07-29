import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
import numpy as np
from characters import *
from esc_functions import *
from hex_functions import *
import binascii
import math

# cd to project base directory
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(os.path.join(dname, '..', '..'))


# SPECIFY FILENAME, PRINTERNAME AND OUTPUTFOLDER
filename = 'test_c88'
# one of the printers for which the header and footer files are available in the 'prns' folder
printer = 'c88'
outputfolder = 'output'

# SET PARAMETERS
# These parameters depend on the specific printer
# printer units can be found by parsing the prn file
# Same with color codes, print a file with all colors and parse it
# other specs can be found by looking in spec sheet or service manual (if available)

# unit parameters
pmgmt = 720
vert = 720
hor = 720
mbase = 2880
nozzles = 59

# set nozzle row numbers (def black = 00)
# should work with c88
black = b'\x00'
magenta = b'\x01'
cyan = b'\x02'
yellow = b'\x04'

# select dot size
d = b'\x10'
# set page method ID
esc_m = ESC_m(b'\x20')
# set uni or bi directional mode
unim = b'\x00'  # 01 uni, 00 bi


# CREATE THE RASTERDATA
# initialize empty byte string containing the rasterdata
raster = b''

# location of raster (in inches)
x = 1       # one inch from left edge of paper
y = 1       # one inch from top edge of paper

# Create the matrix
# width of the matrix (number of droplets in printhead travel direction)
width = 100
matrix = np.zeros((nozzles, width))     # init the matrix as all zeros
# set all rows of the matrix to 3's (large droplets), except for the last 2 rows
matrix[0:58, :] = 3

# Create the raster,
#   First set the x position of the printhead,
#   Print the matrix
raster += ESC_dollar(hor, x) + ESC_i_matrix(black, matrix, spacing=0, fan=0)

# First set the vertical position on the paper, then print the raster as composed in the previous step, add a linefeed
rasterdata = ESC_v(pmgmt, y) + raster + b'\x0c'


# LOAD HEADER AND FOOTER FOR SELECTED PRINTER
header = load_prn_file('prns/' + printer + '/' + printer + '-header.prn')
footer = load_prn_file('prns/' + printer + '/' + printer + '-footer.prn')
# header = b''
# footer = b''

# COMPOSE BODY
body = ESC_Graph() + ESC_Units(pmgmt, vert, hor, mbase) + ESC_Kmode() + \
    ESC_imode(n=b'\x00') + ESC_Umode(unim) + ESC_edot(d) + ESC_Dras(v=240 / 3, h=120 / 3) + \
    ESC_C(pmgmt) + ESC_c(pmgmt) + ESC_S(pmgmt)  # + esc_m

# COMBINE
total = header + body + rasterdata + footer

# CREATE OUTPUT DIR
filename = outputfolder + '/' + filename + '.prn'

# SAVE PRN FILE
save_prn_file(total, filename)
print('DONE!')
print('path: ' + filename)
