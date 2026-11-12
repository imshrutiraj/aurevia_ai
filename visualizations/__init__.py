"""Package shim for the flattened repository.

charts.py lives at the repository root; this package resolves
`visualizations.charts` from there.
"""
import os as _os

__path__ = [_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))]
