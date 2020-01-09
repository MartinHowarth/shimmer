"""Global setup for pytest."""

import os
import sys

SKIP_GUI_TESTS = "SKIP_GUI_TESTS" in os.environ


if SKIP_GUI_TESTS:
    # In CI we don't have GL, so stop pyglet trying to use it by pretending
    # that this is a pyglet doc run.
    setattr(sys, "is_pyglet_doc_run", True)
