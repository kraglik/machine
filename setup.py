try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup


import os.path

readme = ''
here = os.path.abspath(os.path.dirname(__file__))
readme_path = os.path.join(here, 'README.md')
if os.path.exists(readme_path):
    with open(readme_path, 'rb') as stream:
        readme = stream.read().decode('utf8')


setup(
    long_description=readme,
    long_description_content_type='text/markdown',
    name='machine-web',
    version='0.0.2',
    description='A simple plugin-based web framework',
    python_requires='==3.*,>=3.8.0',
    project_urls={'homepage': 'https://github.com/kraglik/machine', 'repository': 'https://github.com/kraglik/machine'},
    author='Igor Kraglik',
    author_email='kraglik.i.d@gmail.com',
    license='BSDv3',
    keywords=['web', 'framework', 'machine'],
    packages=find_packages(),
    package_data={},
    install_requires=[
        'anyio==3.3.2',
        'asgiref==3.4.1',
        'attrs==21.2.0',
        'certifi==2021.5.30',
        'charset-normalizer==2.0.6',
        'click==8.0.1', 'h11==0.12.0',
        'httptools==0.3.0',
        'idna==3.2',
        'ijson==3.1.4',
        'iniconfig==1.1.1',
        'multidict==5.1.0',
        'packaging==21.0',
        'pluggy==1.0.0',
        'py==1.10.0',
        'pyparsing==2.4.7',
        'pytest==6.2.5',
        'requests==2.26.0',
        'sniffio==1.2.0',
        'toml==0.10.2',
        'urllib3==1.26.7',
        'uvicorn==0.15.0',
        'yarl==1.6.3'
    ],
    extras_require={},
)