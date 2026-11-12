"""Package shim for the flattened repository.

The backend modules (resume_parser.py, skill_extractor.py, ...) live at the
repository root. Pointing this package's search path at the root lets the
existing `from backend.x import Y` imports resolve without moving files.
"""
import os as _os

__path__ = [_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))]
