from flask import Flask, request, jsonify
import time

from pywowgen.waworld import waworld


def waapirun(force=False, respath=None, tmppath=None, finpath=None):

    appconfig = {
        "DEBUG": False,
        "SESSION_COOKIE_SECURE": True,
        "REMEMBER_COOKIE_SECURE": True,
        "SESSION_COOKIE_HTTPONLY": True,
        "REMEMBER_COOKIE_HTTPONLY": True,
        "SESSION_COOKIE_SAMESITE": "Strict",
        "MAX_CONTENT_LENGTH": 1024 * 1024 * 100,  # 100mb
    }

    app = Flask(__name__)
    app.config.from_mapping(appconfig)

    @app.route('/api/generate/world', methods=['POST'])
    def api_generate_world_by_config():
        logmsgs = []
        world_config = request.json  # json.loads(request.json)

        try:
            # init new world
            apiworld = waworld()
            apiworld.set(world_config)

            # force overwrite configs
            if force and respath and tmppath and finpath:
                apiworld.config['config_tool']['res_paths'] = respath
                apiworld.config['config_tool']['tmp_path'] = tmppath
                apiworld.config['config_tool']['final_path'] = finpath
                logmsgs.append('{int(time.time())}: enforced paths {str(respath)} {str(tmppath)} {str(tmppath)}')
            # generate worlds objects, register custom maps
            apiworld.generate()

            # save the world and see where it landed
            td = apiworld.save()

            logmsgs.append('{int(time.time())}: {td}')
            print('saved whole world to files in directory: ', td)

            # check the generated worlds maps, returns a graph for cytoscape
            graphdata = apiworld.check_maps()

            return jsonify({
                'log': logmsgs,
                'config': world_config,
                'analysis': graphdata,
            })
        except ValueError as err:
            print(err)
            logmsgs.append('{int(time.time())}: {err}')

            return jsonify({
                'log': logmsgs,
                'config': world_config,
                'analysis': {},
            })

    @app.after_request
    def add_cors_headers(response):
        # white = ['http://localhost:5000', 'http://127.0.0.1:5000']
        # r = request.referrer[:-1]
        # if r in white:
        response.headers.add('Access-Control-Allow-Origin', '*')  # r)
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Headers', 'Cache-Control')
        response.headers.add('Access-Control-Allow-Headers', 'X-Requested-With')
        response.headers.add('Access-Control-Allow-Headers', 'Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, DELETE')
        return response

    app.run(debug=False)

if __name__ == "__main__":
    import doctest

    doctest.testmod(verbose=True)
