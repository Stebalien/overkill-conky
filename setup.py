from setuptools import setup, find_packages
setup(
    name = "overkill-extra-conky",
    version = "0.1",
    install_requires=["overkill"],
    packages = find_packages(),
    author = "Steven Allen",
    author_email = "steven@stebalien.com",
    description = "Conky data source for overkill.",
    namespace_packages = ["overkill", "overkill.extra"],
    license = "GPL3",
    url = "http://stebalien.com"
)