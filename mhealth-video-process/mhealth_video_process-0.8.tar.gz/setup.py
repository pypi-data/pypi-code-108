import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mhealth_video_process",
    version="0.8",
    author="binodtc",
    author_email="binod.thapachhetry@gmail.com",
    description="A pacakge to process video files.",
    url="https://bitbucket.org/mhealthresearchgroup/video-process.git",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
    install_requires=['get-video-properties==0.1.1'],
    package_data={'src\mhealth_video_process':['exiftool.exe']},
    include_package_data=True
)