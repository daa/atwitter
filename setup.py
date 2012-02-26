from distutils.core import setup

setup(name='atwitter',
    version='0.1',
    description='Twitter client for Python mainly intented for Twisted',
    author='Alexander Duryagin',
    author_email='aduryagin@gmail.com',
    url='http://github.com/daa/atwitter/',
    license='MIT',
    platforms='any',
    packages=['atwitter', 'atwitter.adapters'],
)
