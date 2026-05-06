import sys

from modules import simulation

# The major, minor versions of python that our simulation requires
MIN_VER = (3, 9)

if __name__ == "__main__":
    if sys.version_info[:2] < MIN_VER:
        sys.exit("This simulation requires Python {}.{}.".format(*MIN_VER))
    else:
        simulation.run()