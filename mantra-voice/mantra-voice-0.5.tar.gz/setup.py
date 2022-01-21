from distutils.core import setup

# Look man, i'm too lazy so i just copied it from the requirements.txt and did this
install_requires = """
pyttsx3==2.90
gtts==2.2.3
sox==1.4.1
soundfile==0.10.3.post1
sounddevice==0.4.4
""".split()

setup(
    name="mantra-voice",
    packages=["mantra_voice"],
    version="0.5",
    license="MIT",
    description="A speech to text library that builds on top of gTTS and pyttsx3.",
    author="Philippe Mathew",
    author_email="philmattdev@gmail.com",
    url="https://github.com/bossauh/mantra-voice",
    download_url="https://github.com/bossauh/mantra-voice/archive/refs/tags/v_05.tar.gz",
    keywords=["speech", "synthesizer"],
    install_requires=install_requires,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7"
    ]
)
