from distutils.core import setup
from Cython.Build import cythonize
import subprocess as sub

setup(
    ext_modules = cythonize([
        'cutils.pyx', 
    ]),
)

sub.call('mv display/cutils.cpython* cutils.so && rmdir display && rm -r build ', shell=True)
sub.call('rm -f cutils.c ', shell=True)
