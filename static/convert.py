import sys
import os
args = sys.argv
args.pop(0)

name = args[0]
os.system(f"convert {name} {name.split('.')[0]}.webp")
