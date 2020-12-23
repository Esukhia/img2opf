from setuptools import find_packages, setup

setup(
    name="img2opf",
    version="0.0.1",
    packages=find_packages(),
    install_requires=[
        "google-cloud-vision==0.37.0",
    ],
    extras_require={
        "bdrc": [
            "openpecha",
            "boto3==1.16.41",
            "slack-sdk==3.1.0",
            "Pillow==8.0.1",
        ]
    },
)
