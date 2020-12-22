from setuptools import find_packages, setup

setup(
    name="img2opf",
    version="0.0.1",
    packages=find_packages(),
    install_requires=[
        "openpecha",
        "google-cloud-vision==0.37.0",
        "requests==2.22.0",
        "boto3==1.16.41",
        "slack-sdk==3.1.0",
    ],
)
