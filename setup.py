from setuptools import find_packages, setup
setup(name="torminify",
    install_requires=['pyyaml','tornado'],
    version="0.1",
    description="",
    author="Paul Diakov",
    author_email='paul.diakov@gmail.com',
    platforms=["any"],
    license="BSD",
    url="http://github.com/",
    packages=find_packages()
)