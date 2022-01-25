import os
import sys, subprocess

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
    pass

class AppFileAlreadyExistsException(Error):
    """raised if a file by the name of app.py is found in the target directory"""
    pass

class DockerfileAlreadyExistsException(Error):
    """raised if a dockerfile ('dockerfile') already exists in the target directory."""
    pass

class DockerBuilder():
    """
    Prepares required assets and builds a  docker image, with web service, to serve a machine learning model.

    Params:
    model (string) --> the relative filepath to the serialized model file (.pkl)
    imagename (string) --> a name for your docker container image
    """
    def __init__(self, model, *, imagename="modelservice"):
        self.model_path = model
        self.requirements = "requirements.txt"
        self.dependencies = "dependencies"
        self.entry_file = "score.py"
        self.imagename = imagename
        self._prepared = False
        self._api_created = False
        self._image_built = False
        self._cleanup_executed = False
    
    def prepare(self):
        """Prepares the assets for the create_api and build_image steps."""
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pigar"])
        if not os.path.exists(self.requirements):
            raise RequirementsNotExistsException("'requirements.txt' file not found - this file is required in working directory.")
        if not os.path.exists(self.model_path):
            raise NoModelFileException("You must have a serialized model file.")
        if not os.path.exists(self.entry_file):
            raise EntryFileNotFoundException("An entry file named 'score.py' must be included in the base directory.")
        if os.path.exists("app.py"):
            raise AppFileAlreadyExistsException("There is already a file by the name of 'app.py' in your target directory. Please delete or rename this file, then run the command again.")
        if os.path.exists('dockerfile'):
            raise DockerfileAlreadyExistsException("There is already a file by the name of 'dockerfile' in the target directory. Please delete this file and try the command again")

    def create_api(self):
        """this builds the api file"""
        api_constant = """
from flask import Flask, request, jsonify
import score

app = Flask(__name__)

@app.route("/score/", methods=['POST'])
def score_model():
    _json = request.json
    score_results = score.score(_json)
    return jsonify(score_results)

if __name__ == '__main__':
    #run the app
    app.run(host='0.0.0.0', debug=True)"""

        with open("app.txt", 'w') as f:
            f.write(api_constant)
        os.rename("app.txt", "app.py")

    def build_image(self):
        """Build the docker image locally. After this step is run, your image will be viewable in Docker Desktop, and accessible with the 'docker run' command.
        
        Params:
        imagename (string) --> the name you wish to use for the newly-created container image
        """
        commands = ['FROM alpine' + "\n",
        'FROM python:3.7' + '\n',
        "RUN apt-get update -y && apt-get install -y python-pip python-dev python-jinja2 python-flask" + "\n",
        "COPY ./requirements.txt /app/requirements.txt" + "\n",
        "WORKDIR /app" + "\n",
        "RUN pip install -r requirements.txt" + "\n",
        "COPY {} /app".format(self.entry_file) + "\n",
        "COPY {} /app".format(self.model_path) + "\n",
        "COPY {} /app".format(self.requirements) + "\n",
        "COPY ./app.py /app" +"\n",
        'ENTRYPOINT [ "python" ]' + "\n",
        'CMD [ "app.py" ]' + "\n"]

        with open("dockerfile", 'w') as f:
            f.writelines(commands)
        
        print(os.system("docker build -t {}:latest .".format(self.imagename)))
    
    def cleanup(self):
        """deletes temporary assets (if they exist) and leaves working directory in previous state"""
        if os.path.exists("dockerfile"):
            os.remove("dockerfile")
        if os.path.exists("app.py"):
            os.remove("app.py")
    
    def do_all(self):
        """prepares, builds, and cleans up. This is the fastest way to build your images."""
        self.prepare()
        self.create_api()
        self.build_image()
        self.cleanup()
    
    def run(self, port=5000):
        """runs the container image on the specified port
        
        Params:
        port (int, default=5000) --> the desired port on which to run the container."""
        os.system(f"docker run -p {port}:{port}   {self.imagename}")

    def help(self):
        """help method for this class"""
        print("ml_unleash")
        print('To compile and build your invokable REST endpoint inside of a docker container, use the method "do_all"')
        print('To complete each step individually, follow the flow of "prepare" -> "create_api" -> "build_image" -> "cleanup"')
        print('To run the image, use the method "run", and pass the desired port (or leave blank to use localhost:5000)')
