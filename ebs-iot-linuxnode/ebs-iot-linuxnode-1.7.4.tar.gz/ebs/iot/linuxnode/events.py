

import os
from datetime import datetime
from datetime import timedelta
from cached_property import threaded_cached_property_with_ttl
from six.moves.urllib.parse import urlparse
from twisted.internet.task import deferLater
from twisted.internet.threads import deferToThread
from twisted.internet.defer import DeferredSemaphore
from twisted import logger

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Text
from sqlalchemy import DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound

from .basenode import BaseIoTNode
from .resources import CacheableResource
from .mediaplayer import MediaPlayerBusy
from .marquee import MarqueeBusy
from .widgets.pdfplayer import generate_pdf_images

from .constants import WEBRESOURCE
from .constants import TEXT

Base = declarative_base()
metadata = Base.metadata


class WebResourceEventsModel(Base):
    __tablename__ = 'events_1'

    id = Column(Integer, primary_key=True)
    eid = Column(Text, unique=True, index=True)
    etype = Column(Integer)
    resource = Column(Text, index=True)
    start_time = Column(DateTime, index=True)
    duration = Column(Text)
    
    def __repr__(self):
        return "{0:3} {2} {3:.2f} {1}".format(
            self.eid, self.resource, self.etype,
            (self.start_time - datetime.now()).total_seconds()
        )


class TextEventsModel(Base):
    __tablename__ = 'events_2'

    id = Column(Integer, primary_key=True)
    eid = Column(Text, unique=True, index=True)
    etype = Column(Integer)
    resource = Column(Text)
    start_time = Column(DateTime, index=True)
    duration = Column(Integer)
    
    def __repr__(self):
        return "{0:3} {2} {3:.2f} {1}".format(
            self.eid, self.resource, self.etype,
            (self.start_time - datetime.now()).total_seconds()
        )


class ScheduledResourceClass(CacheableResource):
    @threaded_cached_property_with_ttl(ttl=3)
    def next_use(self):
        next_event = self.node.event_manager(WEBRESOURCE).next(
            resource=self.filename)
        if next_event:
            return next_event.start_time
        else:
            return None


class Event(object):
    def __init__(self, manager, eid, etype=None, resource=None,
                 start_time=None, duration=None):
        self._manager = manager
        self._eid = eid

        self._etype = None
        self.etype = etype

        self._resource = None
        self.resource = resource

        self._start_time = None
        self.start_time = start_time

        self._duration = None
        self.duration = duration
        if not self._etype:
            self.load()

    @property
    def eid(self):
        return self._eid

    @property
    def etype(self):
        return self._etype

    @etype.setter
    def etype(self, value):
        if value not in [None, WEBRESOURCE, TEXT]:
            raise ValueError
        self._etype = value

    @property
    def resource(self):
        return self._resource

    @resource.setter
    def resource(self, value):
        if self.etype == WEBRESOURCE:
            self._resource = os.path.basename(urlparse(value).path)
        elif self.etype == TEXT:
            self._resource = value

    @property
    def start_time(self):
        return self._start_time

    @start_time.setter
    def start_time(self, value):
        if not value:
            return
        if isinstance(value, datetime):
            self._start_time = value
        else:
            self._start_time = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')

    @property
    def duration(self):
        return self._duration or None

    @duration.setter
    def duration(self, value):
        self._duration = int(value) if value else None

    def commit(self):
        session = self._manager.db()
        try:
            try:
                eobj = session.query(self._db_model).filter_by(eid=self.eid).one()
            except NoResultFound:
                eobj = self._db_model()
                eobj.eid = self.eid

            eobj.etype = self._etype
            eobj.resource = self.resource
            eobj.start_time = self.start_time
            eobj.duration = self.duration

            session.add(eobj)
            session.flush()
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    def load(self):
        session = self._manager.db()
        try:
            eobj = session.query(self._db_model).filter_by(eid=self._eid).one()
            self.etype = eobj.etype
            self.resource = eobj.resource
            self._start_time = eobj.start_time
            self.duration = eobj.duration
        except:
            session.rollback()
            raise
        finally:
            session.close()

    @property
    def _db_model(self):
        return self._manager.db_model

    def __repr__(self):
        return "{0:3} {2} {3:.2f} {1}".format(
            self.eid, self.resource, self.etype,
            (self.start_time - datetime.now()).total_seconds()
        )


class EventManager(object):
    def __init__(self, node, emid):
        self._emid = emid
        self._node = node
        self._db_engine = None
        self._db = None
        self._db_dir = None
        self._execute_task = None
        self._current_event = None
        self._current_event_resource = None
        self._preprocess_semaphore = None
        self._log = None
        _ = self.db

    @property
    def emid(self):
        return self._emid

    @property
    def log(self):
        if not self._log:
            self._log = logger.Logger(namespace="em.{0}".format(self.emid), source=self)
        return self._log

    @property
    def preprocess_semaphore(self):
        if self._preprocess_semaphore is None:
            self._preprocess_semaphore = DeferredSemaphore(1)
        return self._preprocess_semaphore

    def insert(self, eid, **kwargs):
        event = Event(self, eid, **kwargs)
        event.commit()

    def remove(self, eid):
        session = self.db()
        # print("Trying to remove {0} from edb".format(eid))
        try:
            try:
                eobj = session.query(self.db_model).filter_by(eid=eid).one()
            except NoResultFound:
                return False
            # print("Commiting edel")
            session.delete(eobj)
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()
        return True

    def _pointers(self, cond, resource=None, follow=False):
        session = self.db()
        try:
            r = self.db_get_events(session, resource=resource).all()
        except:
            session.rollback()
            raise
        finally:
            session.close()

        e = None
        l = None
        for e in r:
            if l and cond(l, e):
                break
            l = e
        if l:
            if not follow:
                return Event(self, l.eid)
            else:
                if e:
                    ne = Event(self, e.eid)
                else:
                    ne = None
                return Event(self, l.eid), ne
        if follow:
            return None, None
        else:
            return None

    def previous(self, resource=None, follow=False):
        return self._pointers(
            lambda l, e: e.start_time >= datetime.now(),
            resource=resource, follow=follow
        )

    def next(self, resource=None, follow=False):
        return self._pointers(
            lambda l, e: l.start_time >= datetime.now(),
            resource=resource, follow=follow
        )

    def get(self, eid):
        return Event(self, eid)

    def prune(self):
        # TODO This doesn't work!
        # with self.db as db:
        #     r = db[self.db_table_name].find(start_time={'lt': datetime.now()})
        #     for result in r:
        #         print("Removing {0}".format(r))
        #         self.remove(result['eid'])
        session = self.db()
        try:
            results = self.db_get_events(session).all()
        except:
            session.rollback()
            raise
        finally:
            session.close()

        for result in results:
            if result.start_time >= datetime.now():
                break
            self.log.warn("Pruning missed event {event}", event=result)
            self.remove(result.eid)

    def render(self):
        session = self.db()
        try:
            results = self.db_get_events(session).all()
        except:
            session.rollback()
            raise
        finally:
            session.close()
        for result in results:
            print(Event(self, result.eid))

    def db_get_events(self, session, resource=None):
        q = session.query(self.db_model)
        if resource:
            q = q.filter(
                self.db_model.resource == resource
            )
        q = q.order_by(self.db_model.start_time)
        return q

    @property
    def db_model(self):
        if self._emid == WEBRESOURCE:
            return WebResourceEventsModel
        elif self._emid == TEXT:
            return TextEventsModel

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
        return 'sqlite:///{0}'.format(os.path.join(self.db_dir, 'events.db'))

    @property
    def db_dir(self):
        return self._node.db_dir

    @property
    def current_event(self):
        return self._current_event
    
    @property
    def current_event_resource(self):
        return self._current_event_resource

    def _trigger_event(self, event):
        raise NotImplementedError

    def _finish_event(self, forced):
        if forced:
            self.log.info("Event {eid} was force stopped.",
                          eid=self._current_event)
        else:
            self.log.info("Successfully finished event {eid}",
                          eid=self._current_event)
            self._succeed_event(self._current_event)
        self._current_event = None
        self._current_event_resource = None

    def _succeed_event(self, event):
        raise NotImplementedError

    def _event_scheduler(self):
        event = None
        nevent = None
        le, ne = self.previous(follow=True)
        if le:
            ltd = datetime.now() - le.start_time
            # self.log.debug("S {emid} LTD {ltd}",
            #                ltd=ltd, emid=self._emid)
            if abs(ltd) < timedelta(seconds=3):
                event = le
                nevent = ne
        if not event:
            ne, nne = self.next(follow=True)
            if ne:
                ntd = ne.start_time - datetime.now()
                # self.log.debug("S {emid} NTD {ntd}",
                #                ntd=ntd, emid=self._emid)
                if abs(ntd) < timedelta(seconds=3):
                    event = ne
                    nevent = nne
        if event:
            retry = self._trigger_event(event)
            if retry:
                self._execute_task = deferLater(self._node.reactor, 0.1,
                                                self._event_scheduler)
                return
        self._execute_task = self._event_scheduler_hop(nevent)

    def _event_scheduler_hop(self, next_event=None):
        if not next_event:
            next_event = self.next()
        if not next_event:
            next_start = timedelta(seconds=60)
        else:
            next_start = next_event.start_time - datetime.now()
            # print("Next Start : ", next_start)
            if not next_event or next_start < timedelta(0):
                next_start = timedelta(seconds=60)
            elif next_start > timedelta(seconds=60):
                next_start = timedelta(seconds=60)
        self.log.debug("SCHED {emid} HOP {ns}", emid=self._emid,
                       ns=next_start.seconds)
        return deferLater(self._node.reactor, next_start.seconds,
                          self._event_scheduler)

    def start(self):
        self.log.info("Starting Event Manager {emid} of {name}",
                      emid=self._emid, name=self.__class__.__name__)
        self._event_scheduler()


class TextEventManager(EventManager):
    def _trigger_event(self, event):
        try:
            d = self._node.marquee_play(text=event.resource,
                                        duration=event.duration)
            d.addCallback(self._finish_event)
            self.log.info("Executed Event : {0}".format(event))
            self._current_event = event.eid
            self._current_event_resource = event.resource
        except MarqueeBusy as e:
            # self._node.log.warn("Marquee busy for {event} : {e}",
            #                     event=event, e=e.now_playing)
            return e.collision_count
        self.remove(event.eid)
        self.prune()

    def _succeed_event(self, event):
        try:
            self._node.api_text_success([event])
        except NotImplementedError:
            self.log.warn("Node has no text event success reporter")


class WebResourceEventManager(EventManager):
    def _trigger_event(self, event):
        r = self._node.resource_manager.get(event.resource)
        if r.available:
            try:
                d = self._node.media_play(content=r,
                                          duration=event.duration)
                d.addCallback(self._finish_event)
                self.log.info("Executed Event : {0}".format(event))
                self._current_event = event.eid
                self._current_event_resource = event.resource
            except MediaPlayerBusy as e:
                # self.log.warn("Mediaplayer busy for {event} : {e}",
                #               event=event, e=e.now_playing)
                return e.collision_count
        else:
            self.log.warn("Media not ready for {event}", event=event)
        self.remove(event.eid)
        self.prune()

    def _succeed_event(self, event):
        try:
            self._node.api_media_success([event])
        except NotImplementedError:
            self.log.warn("Node has no media event success reporter")

    def _preprocess_pdf(self, filepath):
        name = os.path.splitext(os.path.basename(filepath))[0]
        target = os.path.join(self._node.temp_dir, name)
        return deferToThread(generate_pdf_images, filepath, target, None)

    def _preprocess_resource(self, maybe_failure, resource):
        if os.path.splitext(resource.filename)[1] == '.pdf':
            self.preprocess_semaphore.run(
                self._preprocess_pdf, resource.filepath
            )

    def _fetch(self):
        self.log.debug("Triggering WebResource Fetch")
        session = self.db()
        try:
            results = self.db_get_events(session).all()
        except:
            session.rollback()
            raise
        finally:
            session.close()
        for e in results:
            if e.start_time - datetime.now() > timedelta(seconds=1200):
                break
            r = self._node.resource_manager.get(e.resource)
            d = self._node.resource_manager.prefetch(
                r, semaphore=self._node.http_semaphore_download
            )
            d.addCallback(self._preprocess_resource, r)
        self._fetch_task = deferLater(self._node.reactor, 600, self._fetch)

    def _fetch_scheduler(self):
        self._fetch()

    def _prefetch(self):
        self.log.debug("Triggering WebResource Prefetch")
        session = self.db()
        try:
            results = self.db_get_events(session).all()
        except:
            session.rollback()
            raise
        finally:
            session.close()
        for e in results:
            if e.start_time - datetime.now() > timedelta(seconds=(3600 * 6)):
                break
            r = self._node.resource_manager.get(e.resource)
            self._node.resource_manager.prefetch(
                r, semaphore=self._node.http_semaphore_background
            )
        self._prefetch_task = deferLater(self._node.reactor, 3600, self._prefetch)

    def _prefetch_scheduler(self):
        self._prefetch()

    def start(self):
        super(WebResourceEventManager, self).start()
        self._fetch_scheduler()
        self._prefetch_scheduler()


class EventManagerMixin(BaseIoTNode):
    def __init__(self, *args, **kwargs):
        self._event_managers = {}
        self._success_api_engine = None
        super(EventManagerMixin, self).__init__(*args, **kwargs)

    def event_manager_install(self, manager):
        self.log.info("Installing Event Manager {1} with emid {0}".format(manager.emid, manager))
        self._event_managers[manager.emid] = manager

    def event_manager(self, emid):
        return self._event_managers[emid]

    @property
    def _cache_trim_exclusions(self):
        if self.event_manager(WEBRESOURCE).current_event_resource:
            return [self.event_manager(WEBRESOURCE).current_event_resource]
        else:
            return []

    def api_media_success(self, events):
        if not self._success_api_engine:
            raise NotImplementedError
        self._success_api_engine.api_media_success(events)

    def api_text_success(self, events):
        if not self._success_api_engine:
            raise NotImplementedError
        self._success_api_engine.api_text_success(events)

    def start(self):
        super(EventManagerMixin, self).start()
        for emid, manager in self._event_managers.items():
            manager.start()
