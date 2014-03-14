from setuptools import setup, find_packages

description="""
Advanced improvement of django-orm with a lot of third-party plugins for use different parts of databases are
not covered by the standard orm. 
"""

long_description = """
If you want to know in detail what it offers for each database, check the documentation.

* **Documentation**: http://readthedocs.org/docs/django-orm/en/latest/
* **Project page**: http://www.niwi.be/post/project-django-orm/
"""

setup(
    name = "django-orm-extensions",
    version = ':versiontools:version:',
    url = 'https://github.com/niwibe/django-orm-extensions',
    license = 'BSD',
    platforms = ['OS Independent'],
    description = description.strip(),
    long_description = long_description.strip(),
    author = 'Andrei Antoukh',
    author_email = 'niwi@niwi.be',
    maintainer = 'Andrei Antoukh',
    maintainer_email = 'niwi@niwi.be',
    packages = find_packages(),
    include_package_data = False,
    install_requires = [
        'psycopg2>=2.4'
    ],
    setup_requires = [
        'versiontools >= 1.9',
    ],
    zip_safe = False,
    classifiers = [
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ]
)
