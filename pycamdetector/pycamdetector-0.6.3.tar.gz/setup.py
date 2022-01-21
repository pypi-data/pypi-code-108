from distutils.core import setup
setup(
  name = 'pycamdetector',         # How you named your package folder (MyLib)
  packages = ['pycamdetector'],   # Chose the same as "name"
  version = '0.6.3',      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'Advanced Computer Vision Library which includes Face Detection, Hand Detection, Pose Estimation, '
                'Object Detection',   # Give a short description about your library
  author = 'Roshaan Mehmood',                   # Type in your name
  author_email = 'roshaan55@gmail.com',      # Type in your E-Mail
  url = 'https://github.com/roshaan55/pycamdetector',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/roshaan55/pycamdetector/archive/refs/tags/v_0.6.3.tar.gz',    # I explain this later on
  keywords = ['pycamdetector', 'handtracking', 'facelandmarks', 'pose-estimation', 'object-detection', 'face-detection'],   # Keywords that define your package best
  install_requires=[            # I get to this in a second
          'opencv-python',
          'mediapipe',
          'numpy'
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3.6',      #Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
  ],
)