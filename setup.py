import os
from setuptools import setup


version = '0.0.1'

readme_file = os.path.join(os.path.dirname(__file__), 'README.rst')
with open(readme_file, 'r') as f:
    long_description = f.read()

setup(
    name='django-metric',
    version=version,
    setup_requires=['pytest-runner', ],
    url='',
    author='',
    author_email='',
    download_url='',
    description="",
    long_description=long_description,
    zip_safe=False,
    packages=[
        'metric',
        'metric.management',
        'metric.migrations',
        'metric.testapp',
        'metric.templatetags',
    ],
    include_package_data=True,
    license='BSD',
    install_requires=[
        'six',
        'django-braces',
        'django-braces',
        'python-dateutil',
        'factory',
        'django-model-utils',
    ],
    tests_require=[
        'mock',
        'django-environ',
        'pytest',
        'pytest-django',
        'factory'
    ],
    classifiers=['Development Status :: 3 - Alpha',
                 'Environment :: Web Environment',
                 'Framework :: Django',
                 'Framework :: Django :: 1.8',
                 'Framework :: Django :: 1.9',
                 'Framework :: Django :: 1.10',
                 'Framework :: Django :: 1.11',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: BSD License',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python',
                 'Programming Language :: Python :: 2.7',
                 'Programming Language :: Python :: 3.4',
                 'Programming Language :: Python :: 3.5',
                 'Programming Language :: Python :: 3.6',
                 ],
    test_suite='tests.main',
)
