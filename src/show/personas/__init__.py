"""Shim compat : ``show.personas`` → ``show.guests.personas``."""

from show.guests.personas import *  # noqa: F403
from show.guests.personas import __all__  # noqa: F401
