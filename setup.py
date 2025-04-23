from setuptools import setup

APP = ['lottery.py']
DATA_FILES = ['config.json']
OPTIONS = {
    'argv_emulation': True,
    'packages': ['docx', 'PIL'],
    'iconfile': 'icon.icns',
    'plist': {
        'CFBundleName': '抽奖系统',
        'CFBundleDisplayName': '抽奖系统',
        'CFBundleGetInfoString': "抽奖系统",
        'CFBundleIdentifier': "com.lottery.app",
        'CFBundleVersion': "1.0.0",
        'CFBundleShortVersionString': "1.0.0",
        'NSHumanReadableCopyright': u"Copyright © 2024, All Rights Reserved"
    }
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
) 