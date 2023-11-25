import setuptools
import os

setuptools.setup(
    name='superflexpy',
    version='1.3.2',
    author='Marco Dal Molin, Fabrizio Fenicia, Dmitri Kavetski',
    author_email='marco.dalmolin.1991@gmail.com',
    description='Framework for building hydrological models',
    long_description=open(os.path.join(os.path.dirname(__file__),
                                       "README.md")).read(),
    long_description_content_type='text/markdown',
    url='https://superflexpy.readthedocs.io/en/latest/',
    license='LGPL',
    packages=setuptools.find_packages(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',  # https://martin-thoma.com/software-development-stages/
        'Topic :: Scientific/Engineering :: Hydrology',
    ],
    install_requires=[
        "numba==0.57.1",
        "numpy==1.24.3"
    ],
)
