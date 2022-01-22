import os
from flask import Blueprint, render_template, request, url_for, flash, redirect, make_response, jsonify
import eisenradio.lib.ghetto_recorder as ghetto
from eisenradio.lib.eisdb import get_db_connection, status_read_status_set, render_picture, get_download_dir, \
    get_post, get_db_path
from eisenradio.eisenutil.eisutil import make_folder, is_in_db_view, remove_blank
from eisenradio.eisenutil.measure import measure_meta, stopped_stations
from eisenradio.eisenutil.analyser import analyser_entry
from eisenradio.eisenutil.tools import delete_all_radios, export_radios, import_radios


# Blueprint Configuration
eisenutil_bp = Blueprint(
    'eisenutil_bp', __name__,
    template_folder='bp_util_templates',
    static_folder='bp_util_static',
    static_url_path='/bp_util_static'
)


@eisenutil_bp.route('/tools', methods=('GET', 'POST'))
def tools():
    if request.method == 'POST':
        request_tuple = request.form
        for form in request_tuple:

            if form == 'post_delete_all_radios':
                rv = delete_all_radios()
                if rv:
                    flash('Successfully deleted!', 'success')
                if not rv:
                    flash('Some were not deleted!', 'warning')

            if form == 'post_export_to_ini':
                rv = export_radios()
                if rv:
                    flash('Successfully exported!', 'success')
                if not rv:
                    flash('Something went wrong', 'warning')

            if form == 'post_inputFile_import':
                request_path = os.path.abspath(request.form['post_inputFile_import'])
                print(f' -   ----  post_inputFile_import - --')
                rv = import_radios(str(request_path))
                if rv:
                    flash('Successfully imported!', 'success')
                if not rv:
                    flash('Something went wrong, text utf-format?', 'warning')
    db_path = get_db_path()
    export_path = os.path.abspath(os.path.dirname(db_path))
    return render_template('bp_util_tools.html',
                           export_path=export_path)


@eisenutil_bp.route('/about', methods=('GET', 'POST'))
def about():
    if request.method == 'POST':
        if request.form['browser']:
            status_read_status_set(True, 'eisen_intern', 'browser_open', '1')
            return redirect(url_for('eisenutil_bp.about'))

    is_browser_on = status_read_status_set(False, 'eisen_intern', 'browser_open', '1')
    download_path = get_download_dir()
    db_path = get_db_path()
    return render_template('bp_util_about.html',
                           is_browser_on=is_browser_on,
                           download_path=download_path,
                           db_path=db_path)


@eisenutil_bp.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        rv_req = request.form['title']
        title = remove_blank(rv_req)
        name_in_db = is_in_db_view(title)
        content = request.form['content']

        if not title:
            flash('Name is required!', 'warning')
            return render_template('bp_util_create.html')
        if name_in_db:
            flash('Name is already used!', 'warning')
            return render_template('bp_util_create.html')
        if not content:
            flash('URL is required!', 'warning')
            return render_template('bp_util_create.html')

        # Image
        if request.files['inputFile']:
            file = request.files['inputFile']
            content_type = file.content_type
            print(f' name {file.name} content-type {file.content_type}')
            try:
                db_img = file.read()
                image = render_picture(db_img, 'encode')
            except Exception as e:
                print(e)
                image = None
                content_type = None
                pass
        else:
            image = None
            content_type = None

        if request.form['text']:
            text = request.form['text']
        else:
            text = None

        conn = get_db_connection()
        posts = conn.execute('SELECT * FROM posts').fetchall()
        # if we later want extra save folders for each radio
        try:
            request_path = posts[0]["download_path"]
        except Exception as e:
            print(e)
            print(' looks like the first radio to create, no save to path set')
            conn.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
        else:
            conn.execute('INSERT INTO posts (title, content, download_path, pic_data, pic_content_type, pic_comment) '
                         'VALUES (?, ?, ?, ?, ?, ?)',
                         (title, content, request_path, image, content_type, text))

        conn.commit()
        conn.close()
        return redirect(url_for('eisenhome_bp.index'))

    return render_template('bp_util_create.html')


@eisenutil_bp.route('/save', methods=('GET', 'POST'))
def save():
    rv = None
    if request.method == 'GET':
        """fail if db empty"""
        try:
            rv = os.path.abspath(get_download_dir())
        except TypeError:
            return render_template('bp_util_save.html', save_to='no-directory-found')
        return render_template('bp_util_save.html', save_to=os.path.abspath(get_download_dir()))

    if request.method == 'POST':
        request_path = os.path.abspath(request.form['Path_Save_To'])

        if not request_path:
            flash('A folder is required!', 'warning')
            try:
                rv = os.path.abspath(get_download_dir())
            except TypeError:
                return render_template('bp_util_save.html', save_to='no-directory-found')
            return render_template('bp_util_save.html', save_to=os.path.abspath(get_download_dir()))

        if request_path:
            made_it = make_folder(request_path)
            if not made_it:
                flash('No folder created! exists or denied', 'warning')
                return render_template('bp_util_save.html', save_to=os.path.abspath(get_download_dir()))

            conn = get_db_connection()
            records = conn.execute('select id from posts').fetchall()
            if not records:
                flash('Noting in Database!', 'warning')
                try:
                    return render_template('bp_util_save.html', save_to=os.path.abspath(get_download_dir()))
                except TypeError:
                    return render_template('bp_util_save.html', save_to='no-row-in-table-create-a-radio')
            for id_num in records:
                # print("Radio Id:", id_num[0])
                conn.execute('UPDATE posts SET download_path = ? WHERE id = ?', (request_path, id_num[0]))
            conn.commit()
            conn.close()

            flash(('Save files to: ' + request_path), "success")
            return redirect(url_for('eisenhome_bp.index'))

        return render_template('bp_util_save.html', save_to=os.path.abspath(get_download_dir()))


@eisenutil_bp.route('/<int:id>/edit', methods=('GET', 'POST'))
def edit(id):
    no_image = False
    post = get_post(id)

    if request.method == 'POST':
        rv_req = request.form['title']
        title = rv_req.replace(" ", "")
        content = request.form['content']

        if not title:
            flash('Title is required!', 'warning')
        # Image, if empty keep db entry as it is
        if request.files['inputFile']:
            file = request.files['inputFile']
            content_type = file.content_type
            print(f' name {file.name} content-type {file.content_type}')
            try:
                db_img = file.read()
                image = render_picture(db_img, 'encode')
            except Exception as e:
                print(e)
                image = None
                content_type = None
                no_image = True
                pass
        else:
            image = None
            content_type = None
            no_image = True

        if request.form['text']:
            text = request.form['text']
            if text == 'None':
                text = ' '
        else:
            text = ' '

        conn = get_db_connection()
        if image:
            conn.execute('UPDATE posts SET title = ?, content = ?, pic_data = ?, pic_content_type = ?, '
                         'pic_comment = ? WHERE id = ?',
                         (title, content, image, content_type, text, id))
        else:
            conn.execute('UPDATE posts SET title = ?, content = ?, pic_comment = ?  WHERE id = ?',
                         (title, content, text, id))

        conn.commit()
        conn.close()
        return redirect(url_for('eisenhome_bp.index'))

    return render_template('bp_util_edit.html', post=post)


@eisenutil_bp.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    url_port = ghetto.GIni.parse_url_simple_url(post["content"])

    return render_template('bp_util_post.html',
                           post=post,
                           url_port=url_port)


@eisenutil_bp.route('/sw')
def stream_watcher():
    resp = make_response("stream watcher    (ಠ_ಠ)")
    return resp


@eisenutil_bp.route('/cache_info', methods=['GET'])
def cache_info():
    json_lists = measure_meta()
    if len(json_lists) == 0:
        json_lists = '-empty-'
    return jsonify({"cache_result": json_lists})


@eisenutil_bp.route('/delete_info', methods=['GET'])
def delete_info():
    json_list = stopped_stations()
    if len(json_list) == 0:
        json_list = '-empty-'
    return jsonify({"stopped_result": json_list})


@eisenutil_bp.route('/analyser', methods=('GET', 'POST'))
def analyser():
    b64encode = '-empty-'
    table_id = request.form['table_id']
    media_chunk, content_type = analyser_entry(table_id)
    if not media_chunk == '-empty-':
        b64encode = render_picture(media_chunk, 'encode')
    # print(f'@eisenutil_bp.route  raw_data {media_chunk}')
    response = make_response(b64encode)
    response.headers.set('Content-Type', 'application/octet')      # not known application/octet or from api
    # response.headers.set('Access-Control-Allow-Origin', '*')
    return response

