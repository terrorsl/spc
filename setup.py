from setuptools import setup, find_packages


setup(
    name="spc",
    version="0.3.0",
    description="Simple PDF create",
    packages=find_packages(),
    install_requires=["reportlab", "mistletoe"],
    entry_points={"console_scripts": ["realpython=reader.__main__:main"]}
)
