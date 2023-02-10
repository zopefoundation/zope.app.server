import sys
from contextlib import contextmanager
from io import StringIO


@contextmanager
def capture_output(stdout=None, stderr=None):
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    sys.stdout = stdout = stdout or StringIO()
    sys.stderr = stderr = stderr or StringIO()
    try:
        yield stdout, stderr
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr
