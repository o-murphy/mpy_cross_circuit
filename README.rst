=========
mpy-cross
=========

mpy-cross is the micropython cross compiler utility, used to pre-compile python files into bytecode (mpy files) suitable for running on your target.

For more details about mpy file / format see https://docs.micropython.org/en/latest/reference/mpyfiles.html

This project compiles mpy-cross for windows, linux and macos and distributes them in python wheels for easy installation on development pc's::
    
    pip install mpy-cross

Version
-------

The release version of this package directly corresponds to the micropython release it's built against.

If a wrapper update is needed for a particular release version, it will be updloaded with a `.postN` version

Weekly releases build against master should be available at: https://gitlab.com/alelec/mpy_cross/pipelines
These will have version numbers that reflect the previous release and the current git hash built against.

Usage
-----
mpy-cross package can be run in various different ways

* As per normal mpy-cross app ::

    mpy-cross my_app.py
    mpy-cross --help

* From python command line ::

    python -m mpy_cross <args>
    python -m mpy_cross --help

* From python code ::

    import mpy_cross

    mpy_cross.run(*args, **kwargs)

    import subprocess
    proc = mpy_cross.run('--version', stdout=subprocess.PIPE)

 where `*args` are arguments passed to mpy-cross, `**kwargs` are arguments to pass to `subprocess.Popen()` internally

* Standalone ::

    # Print out path to actual mpy-cross binary
    python -c "import mpy_cross; print(mpy_cross.mpy_cross)"
    > /home/andrew/.local/share/virtualenvs/mpy_cross-gSGkki0d/lib/python3.5/site-packages/mpy_cross/mpy-cross
    /home/corona/.local/share/virtualenvs/mpy_cross-gSGkki0d/lib/python3.5/site-packages/mpy_cross/mpy-cross --version

Older Version Support
---------------------
This package also supports running mpy-cross in compatibility mode to generage mpy files for older releases of micropython.
Compatibility mode can be specified either by micropython version, eg.::

    mpy-cross --compat 1.19 my_app.py

Or by specifying the bytecode version, eg::

    mpy-cross --bytecode 6 my_app.py
