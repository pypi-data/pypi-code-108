import sys
import traceback
import aml_framework
from routes_common import main

def create():
    app = aml_framework.instance.aml_app(__name__)
    app.register_blueprint(main)
    return app

if __name__ == "__main__":
    app = create()
    app.run(host='0.0.0.0', port=31311)
