import os
from operator import mod
import sys, subprocess
from os.path import exists

class Error(Exception):
    """base error class"""
    pass

class RequirementsNotExistsException(Error):
    """raised if the requirements.txt file is not included in the base directory"""
    pass

class NoModelFileException(Error):
    """raised if a serialized model file is not found in the base directory"""
    pass

class EntryFileNotFoundException(Error):
    """raised if the entry file, with name of 'score.py', is not found in the base directory"""

class Builder():
    def __init__(self, model, *, requirements=None, dependencies=None):
        self.model_path = model
        self.requirements = requirements
        self.dependencies = dependencies
    
    def prepare(self):
        """this is the module that will prepare the assets for building"""
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pigar"])
        if not exists("requirements.txt"):
            raise RequirementsNotExistsException("There is no file named 'requirements.txt'")
        if not exists("*.pkl"):
            raise NoModelFileException("You must have a serialized model file.")
        if not exists("score.py"):
            raise EntryFileNotFoundException("An entry file named 'score.py' must be included in the base directory.")

    def help(self):
        print(os.getcwd())

    def create_api(self):
        """this builds the api file"""
        api_constant = """
    from flask import Flask, request, jsonify
    import score

    app = Flask(__name__)

    @app.route("/score/", methods=['POST'])
    def score():
        _json = request.json
        score_results = score.score(_json)
        return jsonify(score_results)

    if __name__ == '__main__':
        #run the app
        app.run(host='0.0.0.0', debug=False)"""

        with open("app.txt", 'w') as f:
            f.write(api_constant)
        os.rename("app.txt", "app.py")

    def build_image(self):
        commands = ['FROM ubuntu:16.04', 
        "RUN apt-get update -y && apt-get install -y python-pip python-dev python-jinja2 python-flask", 
        "WORKDIR /app",
        "RUN pip install -r requirements.txt",
        "COPY . /app",
        'ENTRYPOINT [ "python" ]',
        'CMD [ "app.py" ]']

        with open("dockerfile", 'w') as f:
            f.writelines(commands)
        
        print(os.system("docker build -t flask-tutorial:latest ."))
    
