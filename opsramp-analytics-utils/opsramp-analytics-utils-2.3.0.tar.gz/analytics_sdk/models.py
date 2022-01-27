import os
import json
import uuid
from datetime import datetime, timedelta

import requests

from sqlalchemy import create_engine, Column, DateTime, String, TEXT, ForeignKey, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

from .constants import DATETIME_FORMAT

engine = create_engine(os.getenv('DB_URL'), pool_recycle=28700)
Session = sessionmaker(bind=engine)
Base = declarative_base()


def generate_uuid():
    return str(uuid.uuid4()).replace('-', '')


def period_mapping(period):
    now = datetime.utcnow()

    if period == 'Last Hour':
        _end_date = now.replace(minute=0, second=0, microsecond=0)
        start_date = (_end_date - timedelta(hours=1)).strftime(DATETIME_FORMAT)
    elif period == 'Last 4 Hours':
        _end_date = now.replace(minute=0, second=0, microsecond=0)
        start_date = (_end_date - timedelta(hours=4)).strftime(DATETIME_FORMAT)
    elif period == 'Last 8 Hours':
        _end_date = now.replace(minute=0, second=0, microsecond=0)
        start_date = (_end_date - timedelta(hours=8)).strftime(DATETIME_FORMAT)
    elif period == 'Last 24 Hours':
        _end_date = now.replace(minute=0, second=0, microsecond=0)
        start_date = (_end_date - timedelta(hours=24)).strftime(DATETIME_FORMAT)
    elif period == 'Last 7 Days':
        _end_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        start_date = (_end_date - timedelta(days=7)).strftime(DATETIME_FORMAT)
    elif period == 'Last 30 Days':
        _end_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        start_date = (_end_date - timedelta(days=30)).strftime(DATETIME_FORMAT)
    else:
        dates = period.split(' - ')
        start_date = datetime.strptime(dates[0], '%m/%d/%y').strftime(DATETIME_FORMAT)
        _end_date = datetime.strptime(dates[1], '%m/%d/%y')

    end_date = _end_date.strftime(DATETIME_FORMAT)

    return start_date, end_date


class DictMixin:
    def to_dict(self, detail_mode=None):
        raw_dict = self.__dict__
        result = {}
        for field in self.Meta.fields:
            val = raw_dict.get(field)
            if val is not None and isinstance(val, datetime):
                result[field] = val.strftime(DATETIME_FORMAT)
            else:
                result[field] = val

        return result


class InstalledApp(Base):
    __tablename__ = 'core_installedapp'

    id = Column(String(32), primary_key=True, default=generate_uuid)
    name = Column(String(250), nullable=False)
    slug = Column(String(100), nullable=False)
    version = Column(String(250), nullable=False)
    available_app_id = Column(String(250), nullable=False)
    app_domain = Column(String(200), nullable=False)
    created = Column(DateTime, default=datetime.utcnow)
    modified = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    analyses = relationship("Analysis", back_populates="app")


class Analysis(Base, DictMixin):
    __tablename__ = 'core_analysis'

    id = Column(String(32), primary_key=True, default=generate_uuid)
    app_id = Column(String(32), ForeignKey('core_installedapp.id'), nullable=False)
    name = Column(String(250), nullable=False)
    params = Column(JSON, nullable=False)
    created = Column(DateTime, default=datetime.utcnow)
    modified = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    tenant_id = Column(String(32))

    app = relationship("InstalledApp", back_populates="analyses", lazy=False)
    runs = relationship("AnalysisRun", back_populates="analysis", passive_deletes=True)
    sends = relationship("AnalysisSend", back_populates="analysis", passive_deletes=True)

    class Meta:
        fields = ('id', 'name', 'params', 'created', 'tenant_id')
        ordering = 'name'

    def run(self, func_compute, user_id, is_saved=False):
        from .utilities import upload_to_s3

        start_date, end_date = period_mapping(self.params['period'])
        result = func_compute(start_date, end_date)

        app_slug = 'anonymous'  # get the app slug
        if self.id:
            with Session() as session:
                analysis = session.query(Analysis).filter_by(id=self.id).first()
            app_slug = analysis.app.slug

        key = f'{app_slug}/run/{generate_uuid()}.json'
        result_url = upload_to_s3(json.dumps(result).encode(), key)

        run = AnalysisRun(
            params={
                'start_date': start_date,
                'end_date': end_date
            },
            analysis_id=self.id,
            triggered_by_id=user_id,
            is_saved=is_saved,
            result_url=result_url,
            date_completed=datetime.utcnow()
        )

        with Session.begin() as session:
            session.add(run)
            session.flush()
            run_id = run.id

        with Session() as session:
            run = session.query(AnalysisRun).filter_by(id=run_id).first()

        return run


class AnalysisRun(Base, DictMixin):
    __tablename__ = 'core_analysisrun'

    id = Column(String(32), primary_key=True, default=generate_uuid)
    analysis_id = Column(String(32), ForeignKey('core_analysis.id', ondelete='CASCADE'))
    params = Column(JSON)
    date_launched = Column(DateTime, default=datetime.utcnow)
    date_completed = Column(DateTime)
    result = Column(JSON)
    result_url = Column(String(300))
    is_saved = Column(Boolean, default=False)
    triggered_by_id = Column(String(32), nullable=False)  # user id

    analysis = relationship("Analysis", back_populates="runs", lazy=False)
    exports = relationship("AnalysisExport", back_populates="run", passive_deletes=True)

    class Meta:
        fields = ('id', 'analysis_id', 'params', 'date_launched', 'date_completed', 'is_saved')
        ordering = '-date_launched'

    def to_dict(self, detail_mode=True):
        resp = super().to_dict()
        resp['analysis_name'] = self.analysis.name

        return resp

    def get_result(self):
        result = {}
        if self.result_url:
            result = requests.get(self.result_url).json()
        elif self.result:  # legacy
            result = self.result

        return result


class AnalysisSend(Base, DictMixin):
    __tablename__ = 'core_analysissend'

    id = Column(String(32), primary_key=True, default=generate_uuid)
    analysis_id = Column(String(32), ForeignKey('core_analysis.id', ondelete='CASCADE'))
    subject = Column(String(200), nullable=False)
    format = Column(String(20), default='pdf')
    schedule = Column(String(50))
    recepients = Column(TEXT)
    message = Column(TEXT)
    attachment = Column(String(500))
    jwt_token = Column(TEXT)
    is_active = Column(Boolean, default=True)
    is_ran = Column(Boolean, default=False)
    last_ran = Column(DateTime, default=datetime.utcnow)
    created = Column(DateTime, default=datetime.utcnow)
    modified = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    analysis = relationship("Analysis", back_populates="sends", lazy=False)

    class Meta:
        fields = ('id', 'analysis_id', 'subject', 'format', 'schedule', 'recepients', 'message',
                  'attachment', 'is_active', 'is_ran', 'last_ran', 'created', 'modified')


class AnalysisExport(Base, DictMixin):
    __tablename__ = 'core_analysisexport'

    id = Column(String(32), primary_key=True, default=generate_uuid)
    run_id = Column(String(32), ForeignKey('core_analysisrun.id', ondelete='CASCADE'))
    url = Column(String(300))
    created = Column(DateTime, default=datetime.utcnow)
    modified = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    run = relationship("AnalysisRun", back_populates="exports", lazy=False)

    class Meta:
        fields = ('id', 'run_id', 'url', 'created', 'modified')
