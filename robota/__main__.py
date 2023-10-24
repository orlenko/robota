import sys

from .command import command
from .repl import loop

if len(sys.argv) == 1 or (len(sys.argv) == 2 and sys.argv[1] == "bash"):
    loop()
    sys.exit(0)

sys.exit(command(*(sys.argv[1:])))
