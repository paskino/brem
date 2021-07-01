"""Simple dvc remote execution.

typical usage

>>>   from brem import BasicRemoteExecutionManager

"""

from distutils.version import LooseVersion
from os.path import dirname, basename, isfile, join
import glob
import sys
import paramiko as pk

if sys.version_info[0] == 2:
    raise ImportError('dvc_x requires Python3. This is Python2.')

if LooseVersion(pk.__version__) < '2.7.2':
    raise ImportError(
        'brem needs paramiko-2.7.2 or later. You have: {:s}'.format(pk.__version__))


# from https://stackoverflow.com/questions/1057431
modules = glob.glob(join(dirname(__file__), "*.py"))
__all__ = [basename(f)[:-3] for f in modules if isfile(f)
           and not f.endswith('__init__.py')]

try:
    from .brem import BasicRemoteExecutionManager
    from .brem import RemoteRunControl
    from .brem import RemoteRunControlSignals
    

except ImportError:
    raise ImportError('error importing brem')
