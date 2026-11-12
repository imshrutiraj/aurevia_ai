"""Package shim for the flattened repository.

db.py and models.py live at the repository root; this package resolves
`database.db` and `database.models` from there.
"""
import os as _os

__path__ = [_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))]
