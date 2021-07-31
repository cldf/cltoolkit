from setuptools import setup, find_packages


setup(
    name='cltoolkit',
    version='0.1.0.dev0',
    description='',
    author='',
    author_email='',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    keywords=['Concepticon v2.5.0'],
    license='MIT',
    url='https://github.com/cldf/cltoolkit',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    entry_points={},
    platforms='any',
    python_requires='>=3.5',
        install_requires=[
        'attrs>=18.2',
        'clldutils>=3.5',
        'csvw>=1.6',
        'pycldf',
        'uritemplate',
        'lingpy>=2.6.5',
        'pyclts>=3.1'
    ],
    extras_require={
        'dev': ['flake8', 'wheel', 'twine'],
        'test': [
            'pytest>=6',
            'pytest-mock',
            'pytest-cov',
            'coverage',
            'pyconcepticon',
        ],
    },
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ],
)
