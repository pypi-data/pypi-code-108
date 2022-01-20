#    See the NOTICE file distributed with this work for additional information
#    regarding copyright ownership.
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#        http://www.apache.org/licenses/LICENSE-2.0
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import json
import logging
import re

import time
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, func, and_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

from ensembl.production.core.perl_utils import dict_to_perl_string, perl_string_to_python

__all__ = ['Result', 'LogMessage', 'Job', 'HiveInstance', 'Analysis']

Base = declarative_base()

logger = logging.getLogger(__name__)


class Analysis(Base):
    __tablename__ = 'analysis_base'

    analysis_id = Column(Integer, primary_key=True)
    logic_name = Column(String)

    def __repr__(self):
        return "<Analysis(analysis_id='%s', logic_name='%s')>" % (
            self.analysis_id, self.logic_name)


class AnalysisData(Base):
    __tablename__ = 'analysis_data'

    analysis_data_id = Column(Integer, primary_key=True)
    data = Column(String)

    def __repr__(self):
        return "<AnalysisData(analysis_data_id='%s', data='%s')>" % (
            self.analysis_data_id, self.data)


class Result(Base):
    __tablename__ = 'result'

    job_id = Column(Integer, primary_key=True)
    output = Column(String)

    def output_dict(self):
        return json.loads(self.output)

    def __repr__(self):
        return "<Result(job_id='%s', output='%s')>" % (
            self.job_id, self.output)


class JobProgress(Base):
    __tablename__ = 'job_progress'

    job_progress_id = Column(Integer, primary_key=True)
    job_id = Column(Integer)
    message = Column(String)

    def __repr__(self):
        return "<JobProgress(job_progress_id='%s', job_id='%s', message='%s')>" % (
            self.job_progress_id, self.job_id, self.message)


class LogMessage(Base):
    __tablename__ = 'log_message'

    log_message_id = Column(Integer, primary_key=True)
    job_id = Column(Integer)
    msg = Column(String)
    status = Column(String)
    message_class = Column(String)
    when_logged = Column(String)

    def __repr__(self):
        return "<LogMessage(log_message_id='%s', msg='%s')>" % (
            self.log_message_id, self.msg)


class Role(Base):
    __tablename__ = 'role'

    role_id = Column(Integer, primary_key=True)
    worker_id = Column(Integer, ForeignKey("worker.worker_id"))

    def __repr__(self):
        return "<Role(role_id='%s', worker_id='%s')>" % (
            self.role_id, self.worker_id)


class Worker(Base):
    __tablename__ = 'worker'

    worker_id = Column(Integer, primary_key=True)
    process_id = Column(String)

    def __repr__(self):
        return "<Worker(worker_id='%s', process_id='%s')>" % (
            self.worker_id, self.process_id)


class Semaphore(Base):
    __tablename__ = 'semaphore'

    semaphore_id = Column(Integer, primary_key=True)
    dependent_job_id = Column(Integer)
    local_jobs_counter = Column(Integer, default=0)

    def __repr__(self):
        return "<Semaphore(semaphore_id = '%s', dependent_job_id='%s', local_jobs_counter='%s')>" % (
            self.semaphore_id, self.dependent_job_id, self.local_jobs_counter)


class Job(Base):
    __tablename__ = 'job'

    job_id = Column(Integer(), ForeignKey("result.job_id"), ForeignKey("log_message.job_id"), primary_key=True,
                    autoincrement=True)
    input_id = Column(String)
    status = Column(String)
    param_id_stack = Column(String, default='')
    prev_job_id = Column(Integer)
    controlled_semaphore_id = Column(Integer, ForeignKey("semaphore.semaphore_id"))
    role_id = Column(Integer, ForeignKey("role.role_id"))

    analysis_id = Column(Integer, ForeignKey("analysis_base.analysis_id"))
    analysis = relationship("Analysis", uselist=False, lazy="joined")

    result = relationship("Result", uselist=False, lazy="joined")

    log_messages = relationship("LogMessage", viewonly=True)
    when_completed = Column(String)

    def __repr__(self):
        return "<Job(job_id='%s', analysis='%s', input_id='%s', status='%s', result='%s', role=%s, when_completed=%s)>" % (
            self.job_id, self.analysis.logic_name, self.input_id, self.status,
            (self.result.output if self.result is not None else None),
            self.role_id if self.result is not None else None,
            self.when_completed)


Session = sessionmaker()


class HiveInstance:
    analysis_dict = dict()

    def __init__(self, url, timeout=3600):
        self.engine = create_engine(url, pool_recycle=timeout, echo=False)
        Session.configure(bind=self.engine)

    def get_job_by_id(self, id):
        """ Retrieve a job given the unique surrogate ID """
        s = Session()
        try:
            job = s.query(Job).filter(Job.job_id == id).first()
            if job is None:
                raise ValueError("Job %s not found" % id)
            job.result
            return job
        finally:
            s.close()

    def get_worker_id(self, id):
        """ Retrieve a worker_id for a given role_id """
        s = Session()
        try:
            return s.query(Role).filter(Role.role_id == id).first()
        finally:
            s.close()

    def get_jobs_failure_msg(self, id):
        """Get failures for all the parent and child jobs"""
        s = Session()
        try:
            failures = {}
            parent_job = self.get_job_by_id(id)
            if parent_job.status == 'FAILED':
                failures[id] = self.get_job_failure_msg_by_id(id).msg
            for child_job in s.query(Job).filter(Job.prev_job_id == id).all():
                if child_job.status == 'FAILED':
                    failures[child_job.job_id] = self.get_job_failure_msg_by_id(child_job.job_id).msg
            return failures
        finally:
            s.close()

    def get_job_failure_msg_by_id(self, id, child=False):
        """ Retrieve a job failure message or job child if exist and if child flag turned on"""
        s = Session()
        job = self.get_job_by_id(id)
        if job is None:
            raise ValueError("Job %s not found" % id)
        if child:
            child_job = self.get_job_child(job)
            if child_job is not None:
                try:
                    return s.query(LogMessage).filter(LogMessage.job_id == child_job.job_id).order_by(
                        LogMessage.log_message_id.desc()).first()
                finally:
                    s.close()
            else:
                try:
                    return s.query(LogMessage).filter(LogMessage.job_id == id).order_by(
                        LogMessage.log_message_id.desc()).first()
                finally:
                    s.close()
        else:
            try:
                return s.query(LogMessage).filter(LogMessage.job_id == id).order_by(
                    LogMessage.log_message_id.desc()).first()
            finally:
                s.close()

    def get_worker_process_id(self, id):
        """ Find a workers process_id """
        s = Session()
        try:
            return s.query(Worker).filter(Worker.worker_id == id).first()
        finally:
            s.close()

    def get_analysis_by_name(self, name):
        """ Find an analysis """
        s = Session()
        try:
            return s.query(Analysis).filter(Analysis.logic_name == name).first()
        finally:
            s.close()

    def create_job(self, analysis_name, input_data):
        """
        Create a job for the supplied analysis and input hash
        The input_data dict is converted to a Perl string before storing
        """
        input_data['timestamp'] = time.ctime()
        analysis = self.get_analysis_by_name(analysis_name)
        if analysis is None:
            raise ValueError("Analysis %s not found" % analysis_name)
        s = Session()
        try:
            job = Job(input_id=dict_to_perl_string(input_data), status='READY', analysis_id=analysis.analysis_id);
            s.add(job)
            s.commit()
            # force load of object
            # FIXME any param in connexion should force the loading.
            job.analysis
            job.result
            return job
        except SQLAlchemyError:
            s.rollback()
            raise
        finally:
            s.close()

    def get_analysis_data_input(self, analysis_data_id):
        """ Get the job input stored in the analysis_data table. Get input from child job if exist"""
        s = Session()
        try:
            input_job = s.query(AnalysisData).filter(AnalysisData.analysis_data_id == analysis_data_id).first()
            return input_job
        finally:
            s.close()

    def get_semaphore_data(self, semaphore_job_id):
        """ Get the job semaphore count if exist"""
        s = Session()
        try:
            semaphore_data = s.query(Semaphore).filter(Semaphore.dependent_job_id == semaphore_job_id).first()
            return semaphore_data
        finally:
            s.close()

    def get_result_for_job_id(self, id, child=False, progress=True, analysis_id=None):
        """ Get result for a given job id. If child flag is turned on and job child exist, get result for child job"""

        job = self.get_job_by_id(id)
        if job is None:
            raise ValueError("Job %s not found" % id)
        if child:
            child_job = self.get_job_child(job)
            if child_job is not None:
                return self.get_result_for_job(child_job, progress=progress)
            else:
                return self.get_result_for_job(job, progress=progress)
        else:
            return self.get_result_for_job(job, progress=progress, analysis_id=analysis_id)

    def get_result_for_job(self, job, progress=False, analysis_id=None):
        """
        Determine if the job has completed. If the job has semaphored children, they are also checked
        Also return progress of jobs, completed and total if flag is on
        """
        result = {"id": job.job_id}
        try:
            if re.search(r"^(_extended_data_id){1}(\s){1}(\d+){1}", job.input_id):
                extended_data = job.input_id.split(" ")
                job_input = self.get_analysis_data_input(extended_data[1])
                result['input'] = perl_string_to_python(job_input.data)

            else:
                result['input'] = perl_string_to_python(job.input_id)
            if job.status == 'DONE' and job.result is not None:
                result['status'] = 'complete'
                result['when_completed'] = job.when_completed
                result['output'] = job.result.output_dict()
            else:
                result['status'] = self.get_job_tree_status(job)
            if progress:
                result['progress'] = self.get_all_jobs_progress(job.job_id, analysis_id=analysis_id)
        except ValueError as e:
            raise ValueError('Cannot retrieve results for job: {}'.format(job.job_id)) from e
        except SQLAlchemyError as e:
            raise ValueError('DB error for job: {}'.format(job.job_id)) from e
        return result

    def get_all_jobs_progress(self, job_id, analysis_id=None):
        """
        Get all jobs from Job table based on given job id and analysis id
        """
        s = Session()
        try:
            results = {'total': 0, 'inprogress': 0, 'completed': 0, 'failed': 0}
            job_pattern = f"{job_id},%"

            if analysis_id:
                jobs = s.query(Job).filter(
                    and_(Job.param_id_stack.ilike(job_pattern), Job.analysis_id == analysis_id)).all()
            else:
                jobs = s.query(Job).filter(Job.param_id_stack.ilike(job_pattern)).all()

            for job in jobs:
                results['total'] += 1
                if job.status == 'DONE':
                    results['completed'] += 1
                elif job.status == 'FAILED':
                    results['failed'] += 1
                else:
                    results['inprogress'] += 1
            return results
        except Exception as e:
            return results
        finally:
            s.close()

    def get_last_job_progress(self, job):
        """ Return last job progress line if exists, else None """
        s = Session()
        try:
            last_job_progress_msg = s.query(JobProgress).filter(JobProgress.job_id == job.job_id).order_by(
                JobProgress.job_progress_id.desc()).first()
            return last_job_progress_msg
        finally:
            s.close()

    def get_jobs_progress(self, job):
        """
        Check data in the job_progress table
        alternatively, get jobs progress for parent and children jobs
        Return number of completed jobs and total of jobs
        If there is data in the job_progress table, return progress message
        """
        s = Session()
        try:
            last_job_progress_msg = s.query(JobProgress).filter(JobProgress.job_id == job.job_id).order_by(
                JobProgress.job_progress_id.desc()).first()
            if last_job_progress_msg is not None:
                total = 10
                complete = s.query(JobProgress).filter(JobProgress.job_id == job.job_id).count()
                return {"complete": complete, "total": total, "message": last_job_progress_msg.message}
            else:
                total = 1
                complete = 0
                parent_job = self.get_job_by_id(job.job_id)
                if parent_job.status == 'DONE':
                    complete += 1
                for child_job in s.query(Job).filter(Job.prev_job_id == job.job_id).all():
                    total += 1
                    if child_job.status == 'DONE':
                        complete += 1
                return {"complete": complete, "total": total}
        finally:
            s.close()

    def get_job_tree_status(self, job):
        """ Recursively check all children of a job """
        # check for semaphores
        semaphore_data = None
        logger.debug("get_job_tree_status :: job: %s", job)
        try:
            s = Session()
            semaphored_job = s.query(Job).filter(Job.prev_job_id == job.job_id and job.status == 'SEMAPHORED').first()
            logger.debug("get_job_tree_status :: semaphored_job: %s", semaphored_job)
            if semaphored_job is not None:
                semaphore_data = self.get_semaphore_data(semaphored_job.job_id)
            logger.debug("get_job_tree_status :: semaphore_data: %s", semaphore_data)
        finally:
            s.close()
        if semaphore_data is not None and semaphore_data.local_jobs_counter > 0:
            return self.check_semaphores_for_job(semaphore_data)
        else:
            if job.status == 'FAILED':
                return 'failed'
            elif job.status == 'READY':
                return 'submitted'
            elif job.status == 'RUN':
                return 'running'
            elif job.status == 'DONE':
                s = Session()
                try:
                    for child_job in s.query(Job).filter(Job.prev_job_id == job.job_id).all():
                        child_status = self.get_job_tree_status(child_job)
                        if child_status != 'complete':
                            return child_status
                    return 'complete'
                finally:
                    s.close()
            else:
                return 'incomplete'

    def get_job_child(self, job):
        """ Get child job for a given parent job """
        s = Session()
        try:
            child_job = s.query(Job).filter(Job.prev_job_id == job.job_id).first()
            return child_job
        finally:
            s.close()

    def get_job_parent(self, job):
        """ Get parent job for a given children job """
        s = Session()
        try:
            parent_job = s.query(Job).filter(Job.job_id == job.prev_job_id).first()
            return parent_job
        finally:
            s.close()

    def get_semaphored_jobs(self, job, status=None):
        """
        Find all jobs that are semaphored children of the nominated job, optional filtering by status
        'complete' indicates that all children completed successfully
        'failed' indicates that at least one child has failed
        'incomplete' indicates that at least one child is running or ready
        """
        s = Session()
        try:
            semaphored_job = s.query(Job).filter(Job.prev_job_id == job.job_id, job.status == 'SEMAPHORED').first()
            semaphore_data = self.get_semaphore_data(semaphored_job.job_id)
            if status is None:
                return s.query(Job).filter(semaphore_data.semaphore_id == Job.controlled_semaphore_id).all()
            else:
                return s.query(Job).filter(semaphore_data.semaphore_id == Job.controlled_semaphore_id,
                                           Job.status == status).all()
        finally:
            s.close()

    def check_semaphores_for_job(self, semaphore_data):
        """ Find all jobs that are semaphored children of the nominated job, and check whether they have completed """
        s = Session()
        try:
            status = 'complete'
            jobs = dict(s.query(Job.status, func.count(Job.status)).filter(
                semaphore_data.semaphore_id == Job.controlled_semaphore_id).group_by(Job.status).all())
            logger.debug("check_semaphores_for_job :: jobs: %s", jobs)
            if jobs.get('FAILED', 0) > 0:
                status = 'failed'
            elif jobs.get('READY', 0) > 0 or jobs.get('RUN', 0) > 0 or jobs.get('SEMAPHORED', 0) > 0:
                status = 'incomplete'
            return status
        finally:
            s.close()

    def get_all_results(self, analysis_name, child=False):
        """Find all jobs from the specified analysis"""
        s = Session()
        try:
            jobs = s.query(Job).join(Analysis).filter(Analysis.logic_name == analysis_name).all()
            if child:
                return list(map(lambda job: self.get_result_for_job(self.get_job_child(job)) if (
                        self.get_job_child(job) is not None) else self.get_result_for_job(job), jobs))
            else:
                return list(map(lambda job: self.get_result_for_job(job), jobs))
        finally:
            s.close()

    def delete_job(self, job, child=False):
        """Delete a job from the hive database
           If child flag turn on, try to delete child job if exist
           Also get parent job if exist and delete it """
        parent_job = self.get_job_parent(job)
        if child:
            child_job = self.get_job_child(job)
            if child_job is not None:
                s = Session()
                try:
                    logger.debug("Deleting children job %s " + child_job.job_id)
                    if child_job.result is not None:
                        s.delete(child_job.result)
                    s.delete(child_job)
                    s.commit()
                except SQLAlchemyError:
                    s.rollback()
                    raise
                finally:
                    s.close()
        if parent_job is not None:
            s = Session()
            try:
                logger.debug("Deleting parent job %s " + parent_job.job_id)
                if parent_job.result is not None:
                    s.delete(parent_job.result)
                s.delete(parent_job)
                s.commit()
            except SQLAlchemyError:
                s.rollback()
                raise
            finally:
                s.close()
        try:
            s = Session()
            logger.debug("Deleting job %s " + job.job_id)
            if job.result is not None:
                s.delete(job.result)
            s.delete(job)
            s.commit()
        except SQLAlchemyError:
            s.rollback()
            raise
        finally:
            s.close()
