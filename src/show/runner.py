"""Shim compat : ``show.runner`` → ``show.runtime.runner``."""

from show.runtime.runner import *  # noqa: F403

if __name__ == "__main__":
    main()
