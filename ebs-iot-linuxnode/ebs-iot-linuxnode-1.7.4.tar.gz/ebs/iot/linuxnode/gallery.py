

import os
from six.moves.urllib.parse import urlparse
from twisted import logger
from twisted.internet.task import deferLater
from twisted.internet.defer import CancelledError

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound

from kivy.uix.relativelayout import RelativeLayout

from .basemixin import BaseMixin
from .basemixin import BaseGuiMixin
from .resources import ASSET
from .widgets.gallery import ImageGallery
from .widgets.pdfplayer import PDFPlayer

WEBRESOURCE = 1

SIDEBAR = 1
PLAYER = 2

Base = declarative_base()
metadata = Base.metadata


class WebResourceGalleryModel(Base):
    __tablename__ = 'gallery_1'

    id = Column(Integer, primary_key=True)
    seq = Column(Integer, unique=True, index=True)
    rtype = Column(Integer)
    resource = Column(Text, index=True)
    duration = Column(Integer)

    def __repr__(self):
        return "{0:3} {1} {2} [{3}]".format(
            self.seq, self.rtype, self.resource, self.duration or ''
        )


class GalleryResource(object):
    def __init__(self, manager, seq=None, rtype=None,
                 resource=None, duration=None):
        self._manager = manager
        self._seq = seq

        self._rtype = None
        self.rtype = rtype

        self._resource = None
        self.resource = resource

        self._duration = duration

        if not self._rtype:
            self.load()

    @property
    def seq(self):
        return self._seq

    @property
    def rtype(self):
        return self._rtype

    @rtype.setter
    def rtype(self, value):
        if value not in [None, WEBRESOURCE]:
            raise ValueError
        self._rtype = value

    @property
    def resource(self):
        return self._resource

    @resource.setter
    def resource(self, value):
        if self._rtype == WEBRESOURCE:
            self._resource = os.path.basename(urlparse(value).path)

    @property
    def duration(self):
        return self._duration

    def commit(self):
        session = self._manager.db()
        try:
            try:
                robj = session.query(self._db_model).filter_by(seq=self.seq).one()
            except NoResultFound:
                robj = self._db_model()
                robj.seq = self.seq

            robj.rtype = self.rtype
            robj.resource = self.resource
            robj.duration = self._duration

            session.add(robj)
            session.commit()
            session.flush()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    def load(self):
        session = self._manager.db()
        try:
            robj = session.query(self._db_model).filter_by(seq=self._seq).one()
            self.rtype = robj.rtype
            self.resource = robj.resource
            self._duration = robj.duration
        except:
            session.rollback()
            raise
        finally:
            session.close()

    @property
    def _db_model(self):
        return self._manager.db_model


class BaseGalleryManager(object):
    def __init__(self, node, gmid, widget, default_duration=4):
        self._gmid = gmid
        self._log = None
        self._node = node
        self._widget = widget
        self._default_duration = default_duration
        self._seq = 0
        self._task = None
        self._items = []

    @property
    def log(self):
        if not self._log:
            self._log = logger.Logger(namespace="gallery.{0}".format(self._gmid),
                                      source=self)
        return self._log

    @property
    def default_duration(self):
        return self._default_duration

    def flush(self, force=False):
        self.log.debug("Flushing gallery resources")
        self._items = []
        if force:
            self._trigger_transition()

    def _load(self, items):
        return items

    def load(self, items):
        self.log.debug("Loading gallery resource list")
        self.flush()
        self._items = self._load(items)

    def add_item(self, item):
        raise NotImplementedError

    def remove_item(self, item):
        raise NotImplementedError

    @property
    def current_seq(self):
        return self._seq

    @property
    def next_seq(self):
        seq = self._seq + 1
        if seq < len(self._items):
            return seq
        elif len(self._items):
            return 0
        else:
            return -1

    def start(self):
        self.log.info("Starting Gallery Manager {gmid} of {name}",
                            gmid=self._gmid, name=self.__class__.__name__)
        self.step()

    def step(self):
        self._seq = self.next_seq
        duration = self._trigger_transition(stopped=False)
        if not duration:
            duration = self.default_duration
        self._task = deferLater(self._node.reactor, duration, self.step)

        def _cancel_handler(failure):
            failure.trap(CancelledError)
        self._task.addErrback(_cancel_handler)
        return self._task

    def _trigger_transition(self, stopped=False):
        # If current_seq is -1, that means the gallery is empty. This may be
        # called repeatedly with -1. Use the returned duration to slow down
        # unnecessary requests. This function should also appropriately handle
        # creating or destroying gallery components.
        if stopped or self.current_seq == -1:
            self._widget.current = None
            return 30
        target = self._items[self.current_seq]
        duration = target.duration
        if target.rtype == WEBRESOURCE:
            fp = self._node.resource_manager.get(target.resource).filepath

            if not os.path.exists(fp):
                self._widget.current = None
                return 10

            if os.path.splitext(fp)[1] == '.pdf':
                fp = PDFPlayer(source=fp, exit_retrace=True,
                               temp_dir=self._node.temp_dir)
                if not target.duration:
                    duration = fp.num_pages * fp.interval

            self._widget.current = fp
        return duration

    def stop(self):
        if self._task:
            self._task.cancel()
        self._trigger_transition(stopped=True)

    def render(self):
        for item in self._items:
            print(item)


class GalleryManager(BaseGalleryManager):
    def __init__(self, *args, **kwargs):
        super(GalleryManager, self).__init__(*args, **kwargs)

        self._db_engine = None
        self._db = None
        self._db_dir = None
        _ = self.db

        self._persistence_load()

    def flush(self, force=False):
        super(GalleryManager, self).flush(force=force)
        session = self.db()
        try:
            results = self.db_get_resources(session).all()
        except NoResultFound:
            session.close()
            return
        try:
            for robj in results:
                session.delete(robj)
                # Orphan the resource so that the cache infrastructure
                # will clear the files as needed
                r = self._node.resource_manager.get(robj.resource)
                r.rtype = None
                r.commit()
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    def _load(self, items):
        _items = []
        for idx, (resource, duration) in enumerate(items):
            robj = GalleryResource(
                self, seq=idx, rtype=WEBRESOURCE,
                resource=resource, duration=duration
            )
            robj.commit()
            _items.append(robj)
            r = self._node.resource_manager.get(resource)
            r.rtype = ASSET
            r.commit()
        self._fetch()
        return _items

    def _persistence_load(self):
        session = self.db()
        try:
            results = self.db_get_resources(session).all()
        except NoResultFound:
            session.close()
            return
        try:
            _items = []
            for robj in results:
                _items.append(GalleryResource(self, robj.seq))
        finally:
            session.close()
        self._items = _items
        self._fetch()

    def db_get_resources(self, session, seq=None):
        q = session.query(self.db_model)
        if seq is not None:
            q = q.filter(
                self.db_model.seq == seq
            )
        else:
            q = q.order_by(self.db_model.seq)
        return q

    @property
    def db_model(self):
        if self._gmid == SIDEBAR:
            return WebResourceGalleryModel

    @property
    def db(self):
        if self._db is None:
            self._db_engine = create_engine(self.db_url)
            metadata.create_all(self._db_engine)
            self._db = sessionmaker(expire_on_commit=False)
            self._db.configure(bind=self._db_engine)
        return self._db

    @property
    def db_url(self):
        return 'sqlite:///{0}'.format(os.path.join(self.db_dir, 'gallery.db'))

    @property
    def db_dir(self):
        return self._node.db_dir

    def _fetch(self):
        self.log.debug("Triggering Gallery Fetch")
        session = self.db()
        try:
            results = self.db_get_resources(session).all()
        except:
            session.rollback()
            raise
        finally:
            session.close()
        for e in results:
            r = self._node.resource_manager.get(e.resource)
            self._node.resource_manager.prefetch(
                r, semaphore=self._node.http_semaphore_download
            )

    def render(self):
        print("----------")
        super(GalleryManager, self).render()
        print("DB Content")
        print("----------")
        session = self.db()
        try:
            results = self.db_get_resources(session).all()
        finally:
            session.close()
        print(results)
        print("----------")


class GalleryMixin(BaseMixin):
    def __init__(self, *args, **kwargs):
        self._gallery_managers = {}
        super(GalleryMixin, self).__init__(*args, **kwargs)

    def gallery_manager(self, gmid):
        if gmid not in self._gallery_managers.keys():
            self.log.info("Initializing gallery manager {gmid}", gmid=gmid)
            self._gallery_managers[gmid] = GalleryManager(self, gmid, self.gui_gallery)
        return self._gallery_managers[gmid]

    def gallery_load(self, items):
        self.gallery_manager(SIDEBAR).load(items)

    def gallery_start(self):
        self.gallery_manager(SIDEBAR).start()

    def gallery_stop(self):
        self.gallery_manager(SIDEBAR).stop()

    @property
    def gui_gallery(self):
        raise NotImplementedError


class GalleryGuiMixin(GalleryMixin, BaseGuiMixin):
    _media_extentions_image = ['.png', '.jpg', '.bmp', '.gif', '.jpeg']

    def __init__(self, *args, **kwargs):
        self._gallery = None
        self._gallery_parent_layout = None
        super(GalleryGuiMixin, self).__init__(*args, **kwargs)

    @property
    def gui_gallery_parent(self):
        if not self._gallery_parent_layout:
            self._gallery_parent_layout = RelativeLayout()
            self.gui_sidebar.add_widget(self._gallery_parent_layout)
        return self._gallery_parent_layout

    def _gui_gallery_sidebar_control(self, *args):
        if self.gui_gallery.visible:
            self.gui_sidebar_show('gallery')
        else:
            self.gui_sidebar_hide('gallery')

    @property
    def gui_gallery(self):
        if not self._gallery:
            params = {'parent_layout': self.gui_gallery_parent}
            if self.config.portrait:
                params['animation_vector'] = (1, 0)
            else:
                params['animation_vector'] = (0, 1)
            self._gallery = ImageGallery(**params)
            self._gallery.bind(visible=self._gui_gallery_sidebar_control)
        return self._gallery

    def gui_setup(self):
        super(GalleryGuiMixin, self).gui_setup()
