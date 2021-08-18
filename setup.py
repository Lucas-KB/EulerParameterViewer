import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="euler-parameter-viewer", 
    version="0.1",
    install_requires = [
        'numpy==1.21.2',
        'PyOpenGL==3.1.5',
        'PyQt5==5.15.4',
        'PyQt5-Qt5==5.15.2',
        'PyQt5-sip==12.9.0',
        'pyqtgraph==0.12.2'
    ],
    maintainer="Lucas Kierulff Balabram",
    author="Lucas Kierulff Balabram",
    author_email="lucaskbalabram@gmail.com",
    description="Simple program to easily visualize Euler parameters.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)