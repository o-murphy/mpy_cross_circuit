import os
import re
import sys
import stat
import subprocess
from glob import glob
from os.path import join, dirname, abspath
from . import versions

__all__ = ['mpy_cross_circuit', 'run']
__pkg_dir = abspath(dirname(__file__))
try:
    mpy_cross_circuit = glob(os.path.join(__pkg_dir, 'mpy-cross-circuit*'))[0]
except IndexError:
    raise SystemExit("Error: No mpy-cross-circuit binary found in: %s" % __pkg_dir)


def set_version(circuitpython, bytecode):
    global mpy_cross_circuit
    vers = versions.mpy_version(circuitpython, bytecode)
    path = join(__pkg_dir, 'archive', vers, 'mpy-cross-circuit*')
    try:
        mpy_cross_circuit = glob(path)[0]
    except IndexError:
        raise SystemExit("Error: No mpy-cross-circuit binary found in: %s" % dirname(path))
    


def fix_perms():
    try:
        st = os.stat(mpy_cross_circuit)
        os.chmod(mpy_cross_circuit, st.st_mode | stat.S_IEXEC)
    except OSError:
        pass


def usage():
    fix_perms()
    p = run("-h", stdout=subprocess.PIPE)
    while True:
        line = p.stdout.readline().decode("utf8")
        if not line:
            break
        print(line, end="")
        if line.strip() == "Options:":
            print("-c <version> : --compat <version> : Run mpy-cross-circuit in compatibility mode for given circuitpython version.")
            print("-b <version> : --bytecode <version> : Output specific bytecode version for use with older circuitpython versions.")


def run(*args, **kwargs):
    fix_perms()
    return subprocess.Popen([mpy_cross_circuit] + list(args), **kwargs)


def main():
    compat = None
    bytever = None 
    pop = []
    argv = sys.argv[1:]
    for i, arg in enumerate(argv):
        a = arg.split("=")
        if a[0] in ("-c", "--compat", "-b", "--bytecode"):
            if compat or bytever:
                raise SystemExit("Error: -b and -c are mutually exclusive.")
            pop.append(i)
            if len(a) > 1:
                val = a[1]
            else:
                val = argv[i + 1]
                pop.append(i + 1)
            if "-c" in a[0]:
                compat = val
            else:
                bytever = val
    for i in reversed(pop):
        argv.pop(i)
    if compat or bytever:
        set_version(compat, bytever)
    
    if "-h" in argv or "--help" in argv:
        usage()
    else:
        sys.exit(run(*argv).wait())
