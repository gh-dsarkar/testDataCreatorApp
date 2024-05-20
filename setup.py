from setuptools import setup

APP = ['main.py']
OPTIONS= {
    'argv_emulation': True

}

setup(
    app=APP,
    options={'py2app':OPTIONS},
    requires=['py2app']

)