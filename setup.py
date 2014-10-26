from setuptools import find_packages, setup
setup(name="torminify",
    install_requires=['pyyaml','tornado'],
    version="0.1.2",
    description="",
    author="Paul Diakov",
    author_email='paul.diakov@gmail.com',
    platforms=["any"],
    license="BSD",
    url="https://github.com/PaulDiakov/torminify",
    packages=find_packages()
)