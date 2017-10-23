import datetime
import demjson
import re
from sqlalchemy import desc
from sqlalchemy.orm import relation
from SpiderKeeper.app import db, Base


class Project(Base):
    __tablename__ = 'sk_project'

    project_name = db.Column(db.String(50))

    @classmethod
    def load_project(cls, project_list):
        for project in project_list:
            existed_project = cls.query.filter_by(project_name=project.project_name).first()
            if not existed_project:
                db.session.add(project)
                db.session.commit()

    def to_dict(self):
        return {
            "project_id": self.id,
            "project_name": self.project_name
        }


class SpiderInstance(Base):
    __tablename__ = 'sk_spider'

    spider_name = db.Column(db.String(100))

    project_id = db.Column(
        db.Integer, db.ForeignKey('sk_project.id', ondelete='CASCADE'), nullable=False,
        index=True
    )
    project = relation(Project)

    @classmethod
    def update_spider_instances(cls, project_id, spider_instance_list):
        for spider_instance in spider_instance_list:
            existed_spider_instance = cls.query.filter_by(
                project_id=project_id, spider_name=spider_instance.spider_name
            ).first()
            if not existed_spider_instance:
                db.session.add(spider_instance)
                db.session.commit()

        for spider in cls.query.filter_by(project_id=project_id).all():
            existed_spider = any(
                spider.spider_name == s.spider_name
                for s in spider_instance_list
            )
            if not existed_spider:
                db.session.delete(spider)
                db.session.commit()

    @classmethod
    def list_spider_by_project_id(cls, project_id):
        return cls.query.filter_by(project_id=project_id).all()

    def to_dict(self):
        return dict(spider_instance_id=self.id,
                    spider_name=self.spider_name,
                    project_id=self.project_id)


class JobPriority:
    LOW, NORMAL, HIGH, HIGHEST = range(-1, 3)


class JobRunType:
    ONETIME = 'onetime'
    PERIODIC = 'periodic'


class JobInstance(Base):
    __tablename__ = 'sk_job_instance'

    spider_name = db.Column(db.String(100), nullable=False, index=True)
    project_id = db.Column(
        db.Integer, db.ForeignKey('sk_project.id', ondelete='CASCADE'), nullable=False,
        index=True
    )
    project = relation(Project)

    tags = db.Column(db.Text)  # job tag(split by , )
    spider_arguments = db.Column(db.Text)  # job execute arguments(split by , ex.: arg1=foo,arg2=bar)
    priority = db.Column(db.Integer)
    desc = db.Column(db.Text)
    cron_minutes = db.Column(db.String(20), default="0")
    cron_hour = db.Column(db.String(20), default="*")
    cron_day_of_month = db.Column(db.String(20), default="*")
    cron_day_of_week = db.Column(db.String(20), default="*")
    cron_month = db.Column(db.String(20), default="*")
    enabled = db.Column(db.Integer, default=0)  # 0/-1
    run_type = db.Column(db.String(20))  # periodic/onetime

    def to_dict(self):
        return dict(
            job_instance_id=self.id,
            project_id=self.project_id,
            spider_name=self.spider_name,
            tags=self.tags.split(',') if self.tags else None,
            spider_arguments=self.spider_arguments,
            priority=self.priority,
            desc=self.desc,
            cron_minutes=self.cron_minutes,
            cron_hour=self.cron_hour,
            cron_day_of_month=self.cron_day_of_month,
            cron_day_of_week=self.cron_day_of_week,
            cron_month=self.cron_month,
            enabled=self.enabled == 0,
            run_type=self.run_type

        )

    @classmethod
    def list_job_instance_by_project_id(cls, project_id):
        return cls.query.filter_by(project_id=project_id).all()


class SpiderStatus:
    PENDING, RUNNING, FINISHED, CANCELED = range(4)


class JobExecution(Base):
    __tablename__ = 'sk_job_execution'

    # Useless field, that should be removed
    project_id = db.Column(db.Integer, nullable=False, index=True)
    service_job_execution_id = db.Column(db.String(50), nullable=False, index=True)
    job_instance_id = db.Column(
        db.Integer, db.ForeignKey('sk_job_instance.id', ondelete='CASCADE'), nullable=False,
        index=True
    )
    job_instance = relation(JobInstance)
    create_time = db.Column(db.DateTime)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    running_status = db.Column(db.Integer, default=SpiderStatus.PENDING)
    running_on = db.Column(db.Text)

    raw_stats = db.Column(db.Text)
    items_count = db.Column(db.Integer)
    warnings_count = db.Column(db.Integer)
    errors_count = db.Column(db.Integer)

    RAW_STATS_REGEX = '\[scrapy\.statscollectors\][^{]+({[^}]+})'

    def process_raw_stats(self):
        if self.raw_stats is None:
            return
        datetime_regex = '(datetime\.datetime\([^)]+\))'
        self.raw_stats = re.sub(datetime_regex, r"'\1'", self.raw_stats)
        stats = demjson.decode(self.raw_stats)
        self.items_count = stats.get('item_scraped_count') or 0
        self.warnings_count = stats.get('log_count/WARNING') or 0
        self.errors_count = stats.get('log_count/ERROR') or 0

    def has_warnings(self):
        return not self.raw_stats or not self.items_count or self.warnings_count

    def has_errors(self):
        return bool(self.errors_count)

    def to_dict(self):
        return {
            'project_id': self.project_id,
            'job_execution_id': self.id,
            'job_instance_id': self.job_instance_id,
            'service_job_execution_id': self.service_job_execution_id,
            'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S') if self.create_time else None,
            'start_time': self.start_time.strftime('%Y-%m-%d %H:%M:%S') if self.start_time else None,
            'end_time': self.end_time.strftime('%Y-%m-%d %H:%M:%S') if self.end_time else None,
            'running_status': self.running_status,
            'running_on': self.running_on,
            'job_instance': self.job_instance,
            'has_warnings': self.has_warnings(),
            'has_errors': self.has_errors(),
            'items_count': self.items_count if self.items_count is not None else '-',
            'warnings_count': self.warnings_count if self.warnings_count is not None else '-',
            'errors_count': self.errors_count if self.errors_count is not None else '-'
        }

    @classmethod
    def find_job_by_service_id(cls, service_job_execution_id):
        return cls.query.filter_by(service_job_execution_id=service_job_execution_id).first()

    @classmethod
    def list_job_by_service_ids(cls, service_job_execution_ids):
        return cls.query.filter(cls.service_job_execution_id.in_(service_job_execution_ids)).all()

    @classmethod
    def list_uncomplete_job(cls):
        return cls.query.filter(cls.running_status != SpiderStatus.FINISHED,
                                cls.running_status != SpiderStatus.CANCELED).all()

    @classmethod
    def list_jobs(cls, project_id, each_status_limit=100):
        result = {}
        result['PENDING'] = [job_execution.to_dict() for job_execution in
                             JobExecution.query.filter_by(project_id=project_id,
                                                          running_status=SpiderStatus.PENDING).order_by(
                                 desc(JobExecution.date_modified)).limit(each_status_limit)]
        result['RUNNING'] = [job_execution.to_dict() for job_execution in
                             JobExecution.query.filter_by(project_id=project_id,
                                                          running_status=SpiderStatus.RUNNING).order_by(
                                 desc(JobExecution.date_modified)).limit(each_status_limit)]
        result['COMPLETED'] = [job_execution.to_dict() for job_execution in
                               JobExecution.query.filter(JobExecution.project_id == project_id).filter(
                                   (JobExecution.running_status == SpiderStatus.FINISHED) | (
                                       JobExecution.running_status == SpiderStatus.CANCELED)).order_by(
                                   desc(JobExecution.date_modified)).limit(each_status_limit)]
        return result

    @classmethod
    def list_run_stats_by_hours(cls, project_id):
        result = {}
        hour_keys = []
        last_time = datetime.datetime.now() - datetime.timedelta(hours=23)
        last_time = datetime.datetime(last_time.year, last_time.month, last_time.day, last_time.hour)
        for hour in range(23, -1, -1):
            time_tmp = datetime.datetime.now() - datetime.timedelta(hours=hour)
            hour_key = time_tmp.strftime('%Y-%m-%d %H:00:00')
            hour_keys.append(hour_key)
            result[hour_key] = 0  # init
        for job_execution in JobExecution.query.filter(JobExecution.project_id == project_id,
                                                       JobExecution.date_created >= last_time).all():
            hour_key = job_execution.create_time.strftime('%Y-%m-%d %H:00:00')
            result[hour_key] += 1
        return [dict(key=hour_key, value=result[hour_key]) for hour_key in hour_keys]
