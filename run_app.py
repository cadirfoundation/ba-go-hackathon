import os
import sys

# Pre-register C-extension binary paths for pandas/numpy under AppLocker
base_pkg = r"C:\Program Files\bago_python\Lib\site-packages"
paths = [
    base_pkg,
    os.path.join(base_pkg, "pandas"),
    os.path.join(base_pkg, "pandas", "_libs"),
    os.path.join(base_pkg, "pandas", "_libs", "tslibs")
]

for p in paths:
    if os.path.exists(p) and hasattr(os, "add_dll_directory"):
        try:
            os.add_dll_directory(p)
        except Exception:
            pass

import pandas as pd
print("Pandas C-Extensions Loaded Successfully!")

import streamlit.web.cli as stcli

if __name__ == "__main__":
    sys.argv = ["streamlit", "run", "app.py"]
    sys.exit(stcli.main())