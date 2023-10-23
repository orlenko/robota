import sys

from .command import command
from .repl import loop

if len(sys.argv) > 1:
    sys.exit(command(*sys.argv[1:]))

loop()
