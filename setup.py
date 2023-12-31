from setuptools import setup

# https://python-packaging.readthedocs.io/en/latest/index.html

with open("README.md", "r") as f:
    description = f.read()

setup(
    author="G Schaeffer",
    author_email="gschaeffer@gmail.com",
    description="Simplified access to Google cloud services",
    include_package_data=True,
    install_requires=[
        "arrow",
        "google-area120-tables",
        "google-cloud-firestore",
        "google-cloud-secret-manager",
        "google-cloud-storage",
        "PyDrive",
    ],
    license="MIT",
    long_description=description,
    long_description_content_type="text/markdown",
    name="googpack",
    packages=["googpack"],
    python_requires=">=3.9",
    url="http://github.com/gschaeffer/goog-pack",
    version="0.0.1",
    zip_safe=False,
)
