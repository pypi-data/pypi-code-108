import os
import sys
from time import sleep

sys.path.insert(0, os.getcwd())

try:
    from uuid import uuid4
    import sanic.request
    import sanic.response
    from sanic.exceptions import Forbidden
    from sanic import Sanic
    from .config import CONFIG
    from . import tasks
    from subprocess import call, Popen
    from multiprocessing import Process
    import asyncio
    import sqlite3
    from contextlib import contextmanager
    import string
    import secrets
    import json
    import hmac
    import hashlib
    import markdown2
    import socket
    from itsdangerous import Signer
    from itsdangerous.exc import BadSignature
    from shutil import rmtree, make_archive
    from unicodedata import normalize
    import re
    import aiofiles
    import logging
    import tempfile
    from pythonjsonlogger import jsonlogger
except ModuleNotFoundError as e:
    sys.exit("Import error: {}. Please refer to the documentation.".format(e))

try:
    assert sys.version_info >= (3, 6)
except AssertionError:
    sys.exit("Please update your python (>= 3.6)")

AUTH_DB_PATH = "{}/auth.db".format(CONFIG["CIRCE_WORKING_DIR"])


@contextmanager
def auth_db(readonly=True):
    """
    Auth DB should be read-only by default. Only CLI needs to write.
    """
    if readonly:
        connection = sqlite3.connect("file:{}?mode=ro".format(AUTH_DB_PATH), uri=True)
    else:
        connection = sqlite3.connect(AUTH_DB_PATH)
    yield connection
    connection.close()


if not os.path.isfile(AUTH_DB_PATH):
    with auth_db(readonly=False) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "CREATE TABLE auth(app_uuid text, app_name text, app_secret text);"
        )
        conn.commit()


async def _write_file(path, body):
    async with aiofiles.open(path, "wb") as f:
        await f.write(body)
        await f.close()


def _secure_filename(filename: str) -> str:
    filename = normalize("NFKD", filename).encode("ascii", "ignore")
    filename = filename.decode("ascii")
    for sep in os.path.sep, os.path.altsep:
        if sep:
            filename = filename.replace(sep, " ")
    _filename_ascii_strip_re = re.compile(r"[^A-Za-z0-9_.-]")
    filename = str(_filename_ascii_strip_re.sub("", "_".join(filename.split()))).strip(
        "._"
    )
    return filename


def _check_request_auth(request: sanic.request, payload=None):
    if not CONFIG["CIRCE_USE_AUTH"]:
        return
    if "Authorization" not in request.headers:
        raise Forbidden("Missing Authorization header")
    try:
        uuid, sent_hmac_hash_digest = request.headers["Authorization"].split(" ")
        uuid = uuid.replace("-", "")
    except ValueError:
        raise Forbidden("Authorization malformed")
    with auth_db() as conn:
        cursor = conn.cursor()
        cursor.execute("select app_secret from auth where app_uuid = ?", (uuid,))
        res = cursor.fetchone()
        if not res:
            raise Forbidden("Access denied")
        secret = res[0]
        if payload:
            hmac_hash = hmac.new(
                secret.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256
            )
        else:
            hmac_hash = hmac.new(secret.encode("utf-8"), request.body, hashlib.sha256)
        if hmac_hash.hexdigest() != sent_hmac_hash_digest:
            raise Forbidden("Access Denied")


def _check_port(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex((host, port))
    if result == 0:
        sock.close()
        sys.exit(
            "Socket {}/{} is not available. Please check your configuration.".format(
                host, port
            )
        )


def _make_homepage():
    tpl = (
        "<!DOCTYPE html>"
        '<html lang="fr"><head><meta charset="UTF-8"/><title>Circe - Transformations de documents</title>'
        "<style>"
        "body{{font-family: sans-serif;color:#495057;}}"
        "pre{{color:#c5c8c6; background-color:#1d1f21;padding:10px;line-height:0.8em;border-radius:5px;}}"
        "@media (min-width: 900px) {{body{{width:800px; margin:auto;}}}}"
        "</style>"
        "</head><body>"
        "{}"
        "</body></html>"
    )
    try:
        working_directory = os.path.dirname(os.path.abspath(__file__))
        return tpl.format(
            markdown2.markdown(
                "\r\n".join(
                    open(working_directory + "/../../README.md", "r").readlines()
                )
            )
        )

    except FileNotFoundError:
        return tpl.format(
            "<h1>Circe</h1>"
            "<h2>API web pour la transformation de documents.</h2>"
            "<p>Voir documentation à "
            '<a href="https://git.unicaen.fr/pdn-certic/circe">https://git.unicaen.fr/pdn-certic/circe</a>.</p>'
        )


STATIC_HOMEPAGE_HTML = _make_homepage()
STATIC_AVAILABLE_TRANSFORMATIONS_JSON = json.dumps(
    tasks.get_transformations_descriptions()
)

###############################
#      WEB SERVER ROUTES      #
###############################
server = Sanic(name="circe", strict_slashes=True)
server.config.REQUEST_TIMEOUT = 60 * 30
server.config.RESPONSE_TIMEOUT = 60 * 30
server.config.KEEP_ALIVE = False


@server.get("/")
async def index(request: sanic.request):
    if CONFIG["CIRCE_ENABLE_WEB_UI"]:
        return sanic.response.redirect("/ui/")
    return sanic.response.html(STATIC_HOMEPAGE_HTML)


@server.get("/transformations/")
async def transformations(request: sanic.request):
    return sanic.response.HTTPResponse(
        STATIC_AVAILABLE_TRANSFORMATIONS_JSON,
        headers=None,
        status=200,
        content_type="application/json",
    )


@server.get("/job/<job_id:str>")
async def job_get(request: sanic.request, job_id: str):
    _check_request_auth(request, job_id)
    if os.path.isfile("{}/queue/{}.tar.gz".format(CONFIG["CIRCE_WORKING_DIR"], job_id)):
        return sanic.response.HTTPResponse("Accepted", status=202)
    result_file_path = "{}/done/{}.tar.gz".format(CONFIG["CIRCE_WORKING_DIR"], job_id)
    if os.path.isfile(result_file_path):
        return await sanic.response.file(result_file_path)
        # file_stream is slow ? bad chunk size ?
        # return await sanic.response.file_stream(result_file_path, chunked=False)
    return sanic.response.HTTPResponse("Not Found", status=404)


@server.post("/job/")
async def job_post(request: sanic.request):
    _check_request_auth(request)
    uuid = uuid4()
    archive_destination_path = "{}/queue/{}.tar.gz".format(
        CONFIG["CIRCE_WORKING_DIR"], uuid.hex
    )
    await _write_file(archive_destination_path, request.body)
    job = tasks.do_transformations(uuid, archive_destination_path)
    if request.args.get("block", None):
        job_done_archive = "{}/done/{}.tar.gz".format(
            CONFIG["CIRCE_WORKING_DIR"], uuid.hex
        )
        while True:
            if os.path.isfile(job_done_archive):
                return await sanic.response.file(job_done_archive)
            await asyncio.sleep(1)
    return sanic.response.text(uuid.hex)


if CONFIG["CIRCE_ENABLE_WEB_UI"]:
    cookie_signer = Signer(CONFIG["CIRCE_WEB_UI_CRYPT_KEY"])

    def _check_request_session(request: sanic.request) -> str:
        try:
            session_id = cookie_signer.unsign(request.cookies.get("sess")).decode(
                "UTF-8"
            )
            return session_id
        except (BadSignature, TypeError):
            raise Forbidden("Bad session")

    @server.get("/ui/")
    async def index(request: sanic.request):
        with open(
            os.path.dirname(os.path.abspath(__file__)) + "/static/index.html", "r"
        ) as f:
            response = sanic.response.html("".join(f.readlines()))
            try:
                session_id = _check_request_session(request)
                dir_to_remove = "{}web_ui_sessions/{}".format(
                    CONFIG["CIRCE_WORKING_DIR"], session_id
                )
                rmtree(dir_to_remove, ignore_errors=True)
            except Forbidden:
                pass
            # recréer nouvelle session à chaque affichage de la homepage
            session_id = uuid4().hex
            future_session_path = "{}web_ui_sessions/{}".format(
                CONFIG["CIRCE_WORKING_DIR"], session_id
            )
            tasks.remove_tree.schedule(
                (future_session_path,),
                delay=CONFIG["CIRCE_WEB_UI_REMOVE_USER_FILES_DELAY"],
            )
            signed = cookie_signer.sign(session_id)
            response.cookies["sess"] = signed.decode("UTF-8")
            return response

    @server.route("/upload/", methods=["POST", "GET"])
    async def upload(request: sanic.request):
        if request.method == "GET":
            return sanic.response.HTTPResponse("[]", status=200)
        session_id = _check_request_session(request)
        uploaded = request.files.get("file")
        if not uploaded:
            return sanic.response.HTTPResponse("Missing file", status=400)
        dir_to_create = "{}web_ui_sessions/{}".format(
            CONFIG["CIRCE_WORKING_DIR"], session_id
        )
        dest_name = _secure_filename(uploaded.name)
        os.makedirs(dir_to_create, exist_ok=True)
        await _write_file(os.path.join(dir_to_create, dest_name), uploaded.body)
        return sanic.response.HTTPResponse(request.files.get("file").name, status=200)

    @server.post("/webui/setjob/")
    async def set_job(request: sanic.request):
        session_id = _check_request_session(request)
        session_dir = "{}web_ui_sessions/{}".format(
            CONFIG["CIRCE_WORKING_DIR"], session_id
        )
        if os.path.isdir(session_dir):
            handler: logging.FileHandler = logging.FileHandler(
                "{}/out.log".format(session_dir)
            )
            handler.setFormatter(
                tasks.CustomJsonFormatter(
                    "%(timestamp)s %(level)s %(name)s %(message)s"
                )
            )
            logger: logging.Logger = logging.Logger("job_logger_{}".format(session_id))
            logger.setLevel(logging.DEBUG)
            logger.addHandler(handler)

            transfos = json.loads(request.body)
            for transfo in transfos:
                if transfo["name"] in tasks.registered_transfos.keys():
                    tasks.registered_transfos[transfo["name"]](
                        session_dir, logger, transfo["options"]
                    )
            zip_path = "{}web_ui_sessions/{}".format(
                CONFIG["CIRCE_WORKING_DIR"], session_id
            )
            make_archive(zip_path, "zip", session_dir)
            tasks.remove_file.schedule(
                (zip_path + ".zip",),
                delay=CONFIG["CIRCE_WEB_UI_REMOVE_USER_FILES_DELAY"],
            )
            rmtree(session_dir, ignore_errors=True)
            return sanic.response.HTTPResponse("ok", status=200)
        return sanic.response.HTTPResponse("Bad Request", status=400)

    @server.get("/webui/fetchjob/")
    async def fetch_job(request: sanic.request):
        session_id = _check_request_session(request)
        job_id = session_id
        result_file_path = "{}web_ui_sessions/{}.zip".format(
            CONFIG["CIRCE_WORKING_DIR"], job_id
        )
        if os.path.isfile(result_file_path):
            return await sanic.response.file(
                result_file_path, filename="{}.zip".format(job_id)
            )
        return sanic.response.HTTPResponse("Not Found", status=404)


###############################
#        CLI COMMANDS         #
###############################


def start_workers(workers: int = CONFIG["CIRCE_WORKERS"]):
    """
    Start job workers
    """
    if CONFIG["CIRCE_IMMEDIATE_MODE"]:
        sys.exit("Can't start workers if CIRCE_IMMEDIATE_MODE=1")
    working_directory = os.path.dirname(os.path.abspath(__file__))
    call(
        ["huey_consumer.py", "circe.tasks.huey", "-w", str(workers)],
        cwd=working_directory,
    )


def serve(
    host=CONFIG["CIRCE_HOST"],
    port=CONFIG["CIRCE_PORT"],
    workers=CONFIG["CIRCE_WORKERS"],
    debug=CONFIG["CIRCE_DEBUG"],
    access_log=CONFIG["CIRCE_ACCESS_LOG"],
    static_dir=None,
):
    """
    Start Circe HTTP server
    """
    _check_port(host, port)
    if static_dir:
        server.static("/static", static_dir, name="static_files")
    else:
        server.static(
            "/static", os.path.dirname(os.path.abspath(__file__)) + "/static/"
        )
    try:
        server.run(
            host=host,
            port=port,
            auto_reload=debug,
            debug=debug,
            workers=workers,
            access_log=access_log,
        )
    except OSError:
        sys.exit("Could not start server. Please check your host/port configuration.")


def run(
    host=CONFIG["CIRCE_HOST"],
    port=CONFIG["CIRCE_PORT"],
    workers=CONFIG["CIRCE_WORKERS"],
    debug=CONFIG["CIRCE_DEBUG"],
):
    """
    Start both HTTP server and job workers
    """
    try:
        _check_port(host, port)
        static_dir = os.path.dirname(os.path.abspath(__file__)) + "/static/"
        http_process = Process(
            target=serve,
            args=(
                host,
                int(port),
                int(workers),
                bool(debug),
                CONFIG["CIRCE_ACCESS_LOG"],
                static_dir,
            ),
        )
        http_process.start()
        if not CONFIG["CIRCE_IMMEDIATE_MODE"]:
            transfo_process = Process(target=start_workers, args=(int(workers),))
            transfo_process.start()
            transfo_process.join()
        http_process.join()
    except KeyboardInterrupt:
        try:
            transfo_process.terminate()
        except NameError:
            pass
        sleep(1)
        try:
            http_process.terminate()
        except NameError:
            pass


def remove_api_access(app_uuid: str):
    """
    Remove access to the API
    """
    app_uuid = app_uuid.replace("-", "")
    with auth_db(readonly=False) as conn:
        cursor = conn.cursor()
        cursor.execute("delete from auth where app_uuid = ?", (str(app_uuid),))
        conn.commit()


def make_api_access(
    app_uuid: "specify app uuid to change existing access. Ignore to create new access." = None,
    title: "Title of access (name of app)." = None,
    out: "output credentials in json format to given file" = None,
):
    """
    Create new app uuid / secret couple for api access.

    """
    alphabet = string.ascii_letters + string.digits + string.punctuation
    secret = "".join(secrets.choice(alphabet) for i in range(32))
    title = title or "untitled app"

    if not app_uuid:
        app_uuid = uuid4()
        with auth_db(readonly=False) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "insert into auth(app_uuid, app_name, app_secret) values (?, ?, ?)",
                (app_uuid.hex, title, secret),
            )
            conn.commit()
    else:
        with auth_db(readonly=False) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "update auth set app_secret = ?, app_name = ? where app_uuid = ?",
                (secret, title, app_uuid.hex),
            )
            conn.commit()

    if out:
        data = {
            "uuid": str(app_uuid.hex),
            "title": title,
            "secret": secret,
            "endpoint": None,
        }
        with open(out, "w") as json_file:
            json_file.write(json.dumps(data, indent=4))

    return """Access granted to {}
uuid    : {}
secret: {}
    """.format(
        title, app_uuid.hex, secret
    )


def list_api_access():
    """
    List all access tokens to the API
    """
    with auth_db() as conn:
        cursor = conn.cursor()
        cursor.execute("select app_uuid, app_secret, app_name from auth")
        for row in cursor:
            print("{} : {}  [{}]".format(row[0], row[1], row[2]))


def list_transformations():
    print(json.dumps(tasks.get_transformations_descriptions(), indent=4))
