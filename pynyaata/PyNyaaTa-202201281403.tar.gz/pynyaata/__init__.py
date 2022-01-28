from asyncio import get_event_loop, set_event_loop, SelectorEventLoop
from functools import wraps
from operator import attrgetter, itemgetter

from flask import redirect, render_template, request, url_for, abort

from . import utils
from .config import app, auth, ADMIN_USERNAME, ADMIN_PASSWORD, MYSQL_ENABLED, APP_PORT, IS_DEBUG, TRANSMISSION_ENABLED
from .connectors import get_instance, run_all, Nyaa
from .connectors.core import ConnectorLang, ConnectorReturn
from .forms import SearchForm, DeleteForm, EditForm, FolderDeleteForm, FolderEditForm

if MYSQL_ENABLED:
    from .config import db
    from .models import AnimeFolder, AnimeTitle, AnimeLink

if TRANSMISSION_ENABLED:
    from .config import transmission


def mysql_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not MYSQL_ENABLED:
            return abort(404)
        return f(*args, **kwargs)

    return decorated_function


def clean_titles():
    db.engine.execute("""
DELETE
FROM anime_title
WHERE id IN (
    SELECT anime_title.id
    FROM anime_title
    LEFT JOIN anime_link ON anime_title.id = anime_link.title_id
    WHERE anime_link.id IS NULL
)
""")


@auth.verify_password
def verify_password(username, password):
    return username == ADMIN_USERNAME and ADMIN_PASSWORD == password


@app.template_filter('boldify')
def boldify(name):
    query = request.args.get('q', '')
    name = utils.boldify(name, query)
    if MYSQL_ENABLED:
        for keyword in db.session.query(AnimeTitle.keyword.distinct()).all():
            if keyword[0].lower() != query.lower():
                name = utils.boldify(name, keyword[0])
    return name


@app.template_filter('flagify')
def flagify(is_vf):
    return ConnectorLang.FR.value if is_vf else ConnectorLang.JP.value


@app.template_filter('colorify')
def colorify(model):
    return get_instance(model.link, model.title.keyword).color


@app.context_processor
def inject_user():
    return dict(mysql_disabled=not MYSQL_ENABLED)


@app.route('/')
def home():
    return render_template('layout.html', search_form=SearchForm(), title='Anime torrents search engine')


@app.route('/search')
def search():
    query = request.args.get('q')
    if not query:
        return redirect(url_for('home'))

    set_event_loop(SelectorEventLoop())
    torrents = get_event_loop().run_until_complete(run_all(query))
    return render_template('search.html', search_form=SearchForm(), connectors=torrents)


@app.route('/latest')
@app.route('/latest/<int:page>')
def latest(page=1):
    set_event_loop(SelectorEventLoop())
    torrents = get_event_loop().run_until_complete(
        run_all('', return_type=ConnectorReturn.HISTORY, page=page)
    )

    results = []
    for torrent in torrents:
        results = results + torrent.data
    for result in results:
        result['self'] = get_instance(result['href'])
    results.sort(key=itemgetter('date'), reverse=True)

    return render_template('latest.html', search_form=SearchForm(), torrents=results, page=page)


@app.route('/list')
@app.route('/list/<url_filters>')
@mysql_required
def list_animes(url_filters='nyaa,yggtorrent'):
    filters = None
    for i, to_filter in enumerate(url_filters.split(',')):
        if not i:
            filters = AnimeLink.link.contains(to_filter)
        else:
            filters = filters | AnimeLink.link.contains(to_filter)

    titles = db.session.query(AnimeTitle, AnimeLink).join(
        AnimeLink).filter(filters).order_by(AnimeTitle.name).all()

    results = {}
    for title, link in titles:
        if title.id not in results:
            results[title.id] = [link]
        else:
            results[title.id].append(link)

    return render_template('list.html', search_form=SearchForm(), titles=results)


@app.route('/admin', methods=['GET', 'POST'])
@mysql_required
@auth.login_required
def admin():
    form = DeleteForm(request.form)

    if form.validate_on_submit():
        link = AnimeLink.query.filter_by(id=form.id.data).first()
        if link:
            form.message = '%s (%s) has been successfully deleted' % (
                link.title.name,
                link.season
            )
            db.session.delete(link)
            db.session.commit()

            title = link.title
            if title and not len(title.links):
                db.session.delete(title)
                db.session.commit()
        else:
            form._errors = {
                'id': ['Id %s was not found in the database' % form.id.data]
            }

    folders = AnimeFolder.query.all()
    for folder in folders:
        for title in folder.titles:
            title.links.sort(key=attrgetter('season'))
        folder.titles.sort(key=attrgetter('name'))

    return render_template('admin/list.html', search_form=SearchForm(), folders=folders, action_form=form)


@app.route('/admin/folder', methods=['GET', 'POST'])
@mysql_required
@auth.login_required
def folder_list():
    form = FolderDeleteForm(request.form)

    if form.validate_on_submit():
        folder = AnimeFolder.query.filter_by(id=form.id.data).first()
        if folder:
            form.message = '%s has been successfully deleted' % folder.name
            db.session.delete(folder)
            db.session.commit()
        else:
            form._errors = {
                'id': ['Id %s was not found in the database' % form.id.data]
            }

    folders = AnimeFolder.query.all()

    return render_template('admin/folder/list.html', search_form=SearchForm(), folders=folders, action_form=form)


@app.route('/admin/folder/edit', methods=['GET', 'POST'])
@app.route('/admin/folder/edit/<int:folder_id>', methods=['GET', 'POST'])
@mysql_required
@auth.login_required
def folder_edit(folder_id=None):
    folder = AnimeFolder.query.filter_by(id=folder_id).first()
    folder = folder if folder else AnimeFolder()
    form = FolderEditForm(
        request.form,
        id=folder.id,
        name=folder.name,
        path=folder.path
    )

    if form.validate_on_submit():
        # Folder
        folder.name = form.name.data
        folder.path = form.path.data
        db.session.add(folder)
        db.session.commit()
        return redirect(url_for('folder_list'))

    return render_template('admin/folder/edit.html', search_form=SearchForm(), action_form=form)


@app.route('/admin/edit', methods=['GET', 'POST'])
@app.route('/admin/edit/<int:link_id>', methods=['GET', 'POST'])
@mysql_required
@auth.login_required
def admin_edit(link_id=None):
    link = AnimeLink.query.filter_by(id=link_id).first()
    link = link if link else AnimeLink()

    folders = AnimeFolder.query.all()
    form = EditForm(
        request.form,
        id=link.id,
        folder=link.title.folder.id if link.title else None,
        name=link.title.name if link.title else None,
        link=link.link,
        season=link.season,
        comment=link.comment,
        keyword=link.title.keyword if link.title else None
    )
    form.folder.choices = [('', '')] + [(g.id, g.name) for g in folders]

    if form.validate_on_submit():
        # Instance for VF tag
        instance = get_instance(form.link.data)

        # Title
        title = AnimeTitle.query.filter_by(id=link.title_id).first()
        title = title if title else AnimeTitle.query.filter_by(
            name=form.name.data
        ).first()
        title = title if title else AnimeTitle()
        title.folder_id = form.folder.data
        title.name = form.name.data
        title.keyword = form.keyword.data.lower()
        db.session.add(title)
        db.session.commit()

        # Link
        link.title_id = title.id
        link.link = form.link.data
        link.season = form.season.data
        link.comment = form.comment.data
        link.vf = instance.is_vf(form.link.data)

        # Database
        db.session.add(link)
        db.session.commit()
        clean_titles()

        # Transmission
        if TRANSMISSION_ENABLED and isinstance(instance, Nyaa):
            if title.folder.path is not None and title.folder.path != '':
                download_url = link.link.replace(
                    '/view/',
                    '/download/'
                ) + '.torrent'
                torrent_path = '%s/%s' % (title.folder.path, title.name)
                torrent = transmission.add_torrent(
                    download_url,
                    download_dir=torrent_path
                )
                transmission.move_torrent_data(torrent.id, torrent_path)
                transmission.start_torrent(torrent.id)

        return redirect(url_for('admin'))

    return render_template('admin/edit.html', search_form=SearchForm(), folders=folders, action_form=form)


def run():
    app.run('0.0.0.0', APP_PORT, IS_DEBUG)
