import os

# cd to project base directory
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(os.path.join(dname, '..'))

print(dname)

print(os.getcwd())
