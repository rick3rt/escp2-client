import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
import binascii
import math
from hex_functions import *
from esc_functions import *
from characters import *
import numpy as np

# cd to project base directory
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(os.path.join(dname, '..', '..'))


# SPECIFY FILENAME, PRINTERNAME AND OUTPUTFOLDER
filename = 'test_p600_high_res'
# one of the printers for which the header and footer files are available in the 'prns' folder
printer = 'p600_hr'
outputfolder = 'output'

# SET PARAMETERS
# These parameters depend on the specific printer
# printer units can be found by parsing the prn file
# Same with color codes, print a file with all colors and parse it
# other specs can be found by looking in spec sheet or service manual (if available)

# Shown parameters should work with R2400 / P600 / R3000
# unit parameters
pmgmt = 2880
vert = 2880
hor = 5760
mbase = 5760
nozzles = 180

# set nozzle row numbers (def black = 00)
# Should work with R2400 and P600
black = b'\x00'
lightBlack = b'\x10'
lightLightBlack = b'\x30'
cyan = b'\x02'
lightCyan = b'\x12'
magenta = b'\x01'
lightMagenta = b'\x11'
yellow = b'\x04'


# set uni or bi directional mode
unim = b'\x00'  # 01 uni, 00 bi


# CREATE THE RASTERDATA
# initialize empty byte string containing the rasterdata

# location of raster (in inches)
x = 1       # one inch from left edge of paper
y = 1       # one inch from top edge of paper

# Create the matrix
# width of the matrix (number of droplets in printhead travel direction)
width = 100
matrix = np.zeros((nozzles, width))     # init the matrix as all zeros
# set all rows of the matrix to 1's (small droplets), except for the last 4 rows
matrix[0:nozzles - 4, :] = 1
# set the last row to 3 for large drops
matrix[-1, :] = 3
# set the row before before the last row to 2
matrix[-3, :] = 2
# print(matrix[:, 1])

# Create the raster,
#   First set the x position of the printhead,
#   Print the matrix
pages = []
page1 = ESC_v(pmgmt, y) + ESC_dollar(hor, x) + ESC_i_matrix(black, matrix, spacing=0, fan=0)
page2 = ESC_v(pmgmt, y) + ESC_dollar(hor, x) + ESC_i_matrix(cyan, matrix, spacing=0, fan=0)

pages.append(page1)
pages.append(page2)

# First set the vertical position on the paper, then print the raster as composed in the previous step, add a linefeed
rasterdata = [page + formFeed() for page in pages]
rasterdata = b''.join(rasterdata)

# LOAD HEADER AND FOOTER FOR SELECTED PRINTER
header = load_prn_file('prns/' + printer + '/' + printer + '-header.prn')
footer = load_prn_file('prns/' + printer + '/' + printer + '-footer.prn')

# COMPOSE BODY
body = ESC_Graph() + ESC_Units(pmgmt, vert, hor, mbase) + ESC_Kmode() + \
    ESC_imode(n=b'\x00') + ESC_Umode(unim) + ESC_edot() + ESC_Dras(b'\x50\x14') + \
    ESC_C(pmgmt) + ESC_c(pmgmt) + ESC_S(pmgmt) + ESC_m(m=b'\x50')

# COMBINE
total = header + body + rasterdata + footer

# CREATE OUTPUT DIR
filename = outputfolder + '/' + filename + '.prn'
# if not os.path.exists(outputfolder):
# os.makedirs(outputfolder)

# SAVE PRN FILE
save_prn_file(total, filename)
print('DONE!')
print('path: ' + filename)
