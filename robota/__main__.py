import os
import sys

from .command import command
from .repl import loop

# print(f"env for dir is ROBOTA_CODE_DIR: {os.getenv('ROBOTA_CODE_DIR')}, and argv is {sys.argv}")

if len(sys.argv) == 1 or (len(sys.argv) == 2 and sys.argv[1] == "repl"):
    loop()
    sys.exit(0)


os.chdir(os.getenv("ROBOTA_CODE_DIR"))
sys.exit(command(*(sys.argv[1:])))
