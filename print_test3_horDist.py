# IMPORTS
import binascii
import math
from hex_functions import *
from esc_functions import *
from characters import *
import numpy as np


# SPECIFY FILENAME, PRINTERNAME AND OUTPUTFOLDER
filename = 'test3_p600'
printer = 'p600'  # one of the printers for which the header and footer files are available in the 'prns' folder
outputfolder = '.'

# SET PARAMETERS
# These parameters depend on the specific printer
# printer units can be found by parsing the prn file
# Same with color codes, print a file with all colors and parse it
# other specs can be found by looking in spec sheet or service manual (if available)

# Shown parameters should work with R2400 / P600 / R3000
# unit parameters
pmgmt = 720
vert = 720
hor = 720
mbase = 2880
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

# select dot size
d = b'\x10'
# set page method ID
esc_m = ESC_m(b'\x20')
# set uni or bi directional mode
unim = b'\x00'  # 01 uni, 00 bi


# CREATE THE RASTERDATA
# create a matrix 180 by 50, with all ones. When providing this to esc_i_matrix, this would result in very closely printed droplets, with a spacing of 1/360" (I think!?)
num_drops_hor = 50
mat = np.ones((nozzles, 50))
# set the last row to 3 for large drops
mat[-1, :] = 3
# set the row before before the last row to 2
mat[-3, :] = 2

# check output matrix
print(mat)


# Create the raster.
# raster1: all color channels next to each other, printhead is expected to only make one passage
# print all colors while holding the printhead on the same location.
allColors = [black, lightBlack, lightLightBlack,
             cyan, lightCyan, magenta, lightMagenta, yellow]

# move to x 1 inch location and:
# let the printhead drop a vertical line for each color
raster1 = b''
x = 1       # one inch from left edge of paper
y = 1.345       # some inches from top edge of paper (doesnt matter)
raster1 += ESC_v(pmgmt, y)
raster1 += ESC_dollar(hor, x)
# keep spacing at 0, fan = 0 and size=1 (size=1 is default)
raster1 += ESC_i_matrix(black, mat, spacing=0, fan=0)

# put all individual rasters together. and close with a 0c
rasterdata = raster1 + b'\x0c'


# LOAD HEADER AND FOOTER FOR SELECTED PRINTER
header = load_prn_file('prns/' + printer + '/' + printer + '-header.prn')
footer = load_prn_file('prns/' + printer + '/' + printer + '-footer.prn')
# header = b''
# footer = b''

# COMPOSE BODY
body = ESC_Graph() + ESC_Units(pmgmt, vert, hor, mbase) + ESC_Kmode() + \
    ESC_imode(n=b'\x00') + ESC_Umode(unim) + ESC_edot(d) + ESC_Dras(v=240/3, h=120/3) + \
    ESC_C(pmgmt) + ESC_c(pmgmt) + ESC_S(pmgmt)  # + esc_m

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
