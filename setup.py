from setuptools import setup, find_packages

setup(
    name             = "mmal-proto",
    description      = "Meteorological Middleware Application Layer pandas bindings",
    url              = "https://github.com/hodgesds/mmbal-pandas",
    version          = "0.0.0",
    author           = "Daniel Hodges",
    author_email     = "hodges.daniel.scott@gmail.com",
    scripts          = [],
    install_requires = [ "pandas", "mmal", "mmal-proto"],
    test_suite       = "",
    tests_require    = [ "tox", "nose" ],
    packages         = find_packages(
        where        = '.',
        exclude      = ('tests*', 'bin*'),
    ),
)
