from setuptools import find_packages, setup
setup(name="torminify",
    install_requires=['pyyaml','tornado'],
    version="0.1.3",
    description="Module for Tornado Web Framework, designed to automate minification of css and js files, easily implement asynchronous loading of scripts and additional stylesheets, and cache compiled tornado templates in memory",
    author="Paul Diakov",
    author_email='paul.diakov@gmail.com',
    platforms=["any"],
    license="BSD",
    url="https://github.com/PaulDiakov/torminify",
    packages=find_packages()
)
