from setuptools import find_packages, setup

setup(
    name='are',
    version='0.0.1',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask',
        'requests_oauthlib',
        'Mastodon.py',
    ],
)

