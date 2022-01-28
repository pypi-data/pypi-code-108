from setuptools import setup, find_packages
def readme():
    with open('README.md') as f:
        README=f.read()
    return README

setup(
      name="Upender_recognizer",
      version="0.0.6",
      description='Converting handwritten (digits) information to digital format',
      long_description= readme(),
      keywords=['handwritten','digits', 'recognition','OCR',],
      long_description_content_type='text/markdown',
      url='https://github.com/UpenderKaveti/Real-time-handwritten-digits-recognition-using-Convolutional-Neural-Network',
      author='Upender_Kaveti',
      author_email='artificalintelligence021@gmail.com',
       classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",],
      install_requires=['pandas','numpy','scikit-learn','scikit-optimize','matplotlib','tensorflow','keras','gdown','opencv-python'],
      packages=find_packages('inside'),
      package_dir={'': 'inside',
      },
      include_package_data=True,
      data_files= None,
      python_requires=">=3.6",
      )