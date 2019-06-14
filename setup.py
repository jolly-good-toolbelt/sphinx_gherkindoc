import os
import setuptools

NAME = 'sphinx-gherkindoc'
SUBDIR_NAME = NAME.replace('-', '_')
DESCRIPTION = 'A tool to convert Gherkin files into Sphinx documentation'
VERSION = None

CONSOLE_SCRIPTS = [
    'sphinx-gherkindoc=sphinx_gherkindoc:main',
    'sphinx-gherkinconfig=sphinx_gherkindoc:config'
]

INSTALL_REQUIRES = [
    'Sphinx>=1.3',
    'sphinx_rtd_theme>=0.3.1',
    'behave>=1.2.6',
    'qecommon_tools>=1.0.0',
    'recommonmark>=0.4.0',
]

EXTRAS_REQUIRE = {}

here = os.path.abspath(os.path.dirname(__file__))

about = {}
if not VERSION:
    with open(os.path.join(here, SUBDIR_NAME, '__version__.py')) as f:
        exec(f.read(), about)
else:
    about['__version__'] = VERSION


setuptools.setup(name=NAME,
                 version=about['__version__'],
                 description=DESCRIPTION,
                 url='https://github.rackspace.com/QualityEngineering/QE-Tools',
                 author='Rackspace QE',
                 author_email='qe-tools-contributors@rackspace.com',
                 license='MIT',
                 entry_points={
                     'console_scripts': CONSOLE_SCRIPTS,
                 },
                 install_requires=INSTALL_REQUIRES,
                 packages=setuptools.find_packages(),
                 include_package_data=True,
                 zip_safe=False,
                 extras_require=EXTRAS_REQUIRE,
                 )
