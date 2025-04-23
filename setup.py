import os
import io
import re
import sys
from setuptools import setup
from wheel.bdist_wheel import bdist_wheel as _bdist_wheel

# Use to re-release an updated wrapper for a particular mpy version
post_version = os.environ.get('RE_RELEASE', 0)

# Use to override automatic platform_tag
platform_tag = os.environ.get('PLATFORM_TAG', None)

usage_template = """
mpy-cross options
-----------------
 ::

"""

if '--usage' in sys.argv:
    idx = sys.argv.index('--usage')
    usage_path = sys.argv[idx + 1]

    # Remove args to prevent setuptools parsing them
    sys.argv.pop(idx)
    sys.argv.pop(idx)

    with open(usage_path, 'r') as usage_file:
        usage = usage_file.read()

    usage = usage.split('\n')
    usage_0 = re.sub(r'^(usage:) .*(mpy-cross .*)$', r'\1 \2', usage[0])
    usage = [usage_0] + usage[1:]
    usage_desc = usage_template + '\n'.join(('    %s' % line for line in usage))
else:
    usage_desc = ''


class bdist_wheel(_bdist_wheel):
    def get_tag(self):
        global platform_tag
        rv = _bdist_wheel.get_tag(self)
        platform_tag = rv[-1] if platform_tag is None else platform_tag
        if len(rv) == 3:
            return ['py2.py3', 'none', platform_tag]
        platform_tag = rv[2:] if platform_tag is None else ['none', *platform_tag.split('-')]
        return ['py2.py3'] + list(platform_tag)[-2:]

    def finalize_options(self):
        _bdist_wheel.finalize_options(self)
        self.root_is_pure = False


with io.open('README.rst', encoding='utf8') as readme:
    long_description = readme.read() + usage_desc


# The version consists of <wrapper_version>+<micropython_version> for mpy release
# or <wrapper_version>+<micropython_git_hash> for master build
def version():

    def post_scheme(version):
        global post_version
        tail = ''
        if version.distance:
            tail = f"+{version.node}"
            return tail 
        else:
            post = (f".post{post_version}") if post_version else ''
            return post

    # def mpy_scheme(version):
    #     return str(version.tag if not version.distance else version.node)

    return {#'version_scheme': mpy_scheme,
            'local_scheme': post_scheme,
            'root': 'micropython'}

setup(
    name='mpy_cross',
    use_scm_version=version(),  # Generate version number from git commit/tags
    description='micropython mpy-cross distribution',
    long_description=long_description,
    url="https://gitlab.com/alelec/mpy_cross",
    author="Damien George",
    author_email="contact@micropython.org",
    maintainer="Andrew Leech",
    maintainer_email="andrew@alelec.net",
    license='MIT',
    packages=['mpy_cross'],
    setup_requires=['setuptools_scm==3.5.0', 'wheel'],
    package_data={'': ['mpy-cross*', 'archive/**']},
    cmdclass={'bdist_wheel': bdist_wheel},
    entry_points = {
        'console_scripts': [
            'mpy-cross=mpy_cross:main'
        ],
    },
)
