import os
import glob
import sys

print("Python executable:", sys.executable)
print("Current working directory:", os.getcwd())

files = glob.glob("*.xls")
print(f"Found {len(files)} xls files using glob *.xls")
for f in files:
    print(f)

print("\nListing directory using os.listdir:")
for f in os.listdir("."):
    if f.endswith(".xls"):
        print(f)

try:
    import pandas as pd
    print("\nPandas is installed. Version:", pd.__version__)
except ImportError:
    print("\nPandas is NOT installed.")

try:
    import xlrd
    print("xlrd is installed. Version:", xlrd.__version__)
except ImportError:
    print("xlrd is NOT installed.")

try:
    import openpyxl
    print("openpyxl is installed. Version:", openpyxl.__version__)
except ImportError:
    print("openpyxl is NOT installed.")
