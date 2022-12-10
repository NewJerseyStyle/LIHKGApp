from setuptools import setup

setup(
	name='lihkg',
	version='0.1',
	description='A Terminal App to browse LIHKG',
	url='https://github.com/NewJerseyStyle/LIHKGApp',
	author='David',
	author_email='david@sabie.ai',
	install_requires=['pyppeteer',
					  'pyppeteer-stealth',
					  'nest-asyncio',
					  ],
	scripts=['lihkg.py']
)