from setuptools import setup, find_packages

setup(
    name="orapy_chart",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "base64",
        "uuid",
        "os",
    ],
    python_requires=">=3.8",
    include_package_data=True,
    description="Chart utilities for Oracle AWR/ASH visualization",
    author="Your Name",
    author_email="your@email.com",
    url="https://github.com/yourname/orapy_chart",  # nếu có
)
