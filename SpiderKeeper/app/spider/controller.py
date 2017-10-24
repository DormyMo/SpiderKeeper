import datetime
import os
import tempfile

import flask_restful
import requests
from flask import Blueprint, request, Response
from flask import abort, url_for
from flask import flash
from flask import redirect
from flask import render_template
from flask import session
from flask_restful_swagger import swagger
from sqlalchemy import func
from werkzeug.utils import secure_filename

from SpiderKeeper.app import db, api, agent, app
from SpiderKeeper.app.spider.model import JobInstance, Project, JobExecution, SpiderInstance, \
    JobRunType

api_spider_bp = Blueprint('spider', __name__)

'''
========= api =========
'''


class ProjectCtrl(flask_restful.Resource):
    @swagger.operation(
        summary='list projects',
        parameters=[])
    def get(self):
        return [project.to_dict() for project in Project.query.all()]

    @swagger.operation(
        summary='add project',
        parameters=[{
            "name": "project_name",
            "description": "project name",
            "required": True,
            "paramType": "form",
            "dataType": 'string'
        }])
    def post(self):
        project_name = request.form['project_name']
        project = Project()
        project.project_name = project_name
        db.session.add(project)
        db.session.commit()
        return project.to_dict()


class SpiderCtrl(flask_restful.Resource):
    @swagger.operation(
        summary='list spiders',
        parameters=[{
            "name": "project_id",
            "description": "project id",
            "required": True,
            "paramType": "path",
            "dataType": 'int'
        }])
    def get(self, project_id):
        return [spider_instance.to_dict() for spider_instance in
                SpiderInstance.query.filter_by(project_id=project_id).all()]


class SpiderDetailCtrl(flask_restful.Resource):
    @swagger.operation(
        summary='spider detail',
        parameters=[{
            "name": "project_id",
            "description": "project id",
            "required": True,
            "paramType": "path",
            "dataType": 'int'
        }, {
            "name": "spider_id",
            "description": "spider instance id",
            "required": True,
            "paramType": "path",
            "dataType": 'int'
        }])
    def get(self, project_id, spider_id):
        spider_instance = SpiderInstance.query.filter_by(project_id=project_id, id=spider_id).first()
        return spider_instance.to_dict() if spider_instance else abort(404)

    @swagger.operation(
        summary='run spider',
        parameters=[{
            "name": "project_id",
            "description": "project id",
            "required": True,
            "paramType": "path",
            "dataType": 'int'
        }, {
            "name": "spider_id",
            "description": "spider instance id",
            "required": True,
            "paramType": "path",
            "dataType": 'int'
        }, {
            "name": "spider_arguments",
            "description": "spider arguments",
            "required": False,
            "paramType": "form",
            "dataType": 'string'
        }, {
            "name": "priority",
            "description": "LOW: -1, NORMAL: 0, HIGH: 1, HIGHEST: 2",
            "required": False,
            "paramType": "form",
            "dataType": 'int'
        }, {
            "name": "tags",
            "description": "spider tags",
            "required": False,
            "paramType": "form",
            "dataType": 'string'
        }, {
            "name": "desc",
            "description": "spider desc",
            "required": False,
            "paramType": "form",
            "dataType": 'string'
        }])
    def put(self, project_id, spider_id):
        spider_instance = SpiderInstance.query.filter_by(project_id=project_id, id=spider_id).first()
        if not spider_instance: abort(404)
        job_instance = JobInstance()
        job_instance.spider_name = spider_instance.spider_name
        job_instance.project_id = project_id
        job_instance.spider_arguments = request.form.get('spider_arguments')
        job_instance.desc = request.form.get('desc')
        job_instance.tags = request.form.get('tags')
        job_instance.run_type = JobRunType.ONETIME
        job_instance.priority = request.form.get('priority', 0)
        job_instance.enabled = -1
        db.session.add(job_instance)
        db.session.commit()
        agent.start_spider(job_instance)
        return True


JOB_INSTANCE_FIELDS = [column.name for column in JobInstance.__table__.columns]
JOB_INSTANCE_FIELDS.remove('id')
JOB_INSTANCE_FIELDS.remove('date_created')
JOB_INSTANCE_FIELDS.remove('date_modified')


class JobCtrl(flask_restful.Resource):
    @swagger.operation(
        summary='list job instance',
        parameters=[{
            "name": "project_id",
            "description": "project id",
            "required": True,
            "paramType": "path",
            "dataType": 'int'
        }])
    def get(self, project_id):
        return [job_instance.to_dict() for job_instance in
                JobInstance.query.filter_by(run_type="periodic", project_id=project_id).all()]

    @swagger.operation(
        summary='add job instance',
        notes="json keys: <br>" + "<br>".join(JOB_INSTANCE_FIELDS),
        parameters=[{
            "name": "project_id",
            "description": "project id",
            "required": True,
            "paramType": "path",
            "dataType": 'int'
        }, {
            "name": "spider_name",
            "description": "spider_name",
            "required": True,
            "paramType": "form",
            "dataType": 'string'
        }, {
            "name": "spider_arguments",
            "description": "spider_arguments,  split by ','",
            "required": False,
            "paramType": "form",
            "dataType": 'string'
        }, {
            "name": "desc",
            "description": "desc",
            "required": False,
            "paramType": "form",
            "dataType": 'string'
        }, {
            "name": "tags",
            "description": "tags , split by ','",
            "required": False,
            "paramType": "form",
            "dataType": 'string'
        }, {
            "name": "run_type",
            "description": "onetime/periodic",
            "required": False,
            "paramType": "form",
            "dataType": 'string'
        }, {
            "name": "priority",
            "description": "LOW: -1, NORMAL: 0, HIGH: 1, HIGHEST: 2",
            "required": False,
            "paramType": "form",
            "dataType": 'int'
        }, {
            "name": "cron_minutes",
            "description": "@see http://apscheduler.readthedocs.io/en/latest/modules/triggers/cron.html",
            "required": False,
            "paramType": "form",
            "dataType": 'string'
        }, {
            "name": "cron_hour",
            "description": "",
            "required": False,
            "paramType": "form",
            "dataType": 'string'
        }, {
            "name": "cron_day_of_month",
            "description": "",
            "required": False,
            "paramType": "form",
            "dataType": 'string'
        }, {
            "name": "cron_day_of_week",
            "description": "",
            "required": False,
            "paramType": "form",
            "dataType": 'string'
        }, {
            "name": "cron_month",
            "description": "",
            "required": False,
            "paramType": "form",
            "dataType": 'string'
        }])
    def post(self, project_id):
        post_data = request.form
        if post_data:
            job_instance = JobInstance()
            job_instance.spider_name = post_data['spider_name']
            job_instance.project_id = project_id
            job_instance.spider_arguments = post_data.get('spider_arguments')
            job_instance.desc = post_data.get('desc')
            job_instance.tags = post_data.get('tags')
            job_instance.run_type = post_data['run_type']
            job_instance.priority = post_data.get('priority', 0)
            if job_instance.run_type == "periodic":
                job_instance.cron_minutes = post_data.get('cron_minutes') or '0'
                job_instance.cron_hour = post_data.get('cron_hour') or '*'
                job_instance.cron_day_of_month = post_data.get('cron_day_of_month') or '*'
                job_instance.cron_day_of_week = post_data.get('cron_day_of_week') or '*'
                job_instance.cron_month = post_data.get('cron_month') or '*'
            db.session.add(job_instance)
            db.session.commit()
            return True


class JobDetailCtrl(flask_restful.Resource):
    @swagger.operation(
        summary='update job instance',
        notes="json keys: <br>" + "<br>".join(JOB_INSTANCE_FIELDS),
        parameters=[{
            "name": "project_id",
            "description": "project id",
            "required": True,
            "paramType": "path",
            "dataType": 'int'
        }, {
            "name": "job_id",
            "description": "job instance id",
            "required": True,
            "paramType": "path",
            "dataType": 'int'
        }, {
            "name": "spider_name",
            "description": "spider_name",
            "required": False,
            "paramType": "form",
            "dataType": 'string'
        }, {
            "name": "spider_arguments",
            "description": "spider_arguments,  split by ','",
            "required": False,
            "paramType": "form",
            "dataType": 'string'
        }, {
            "name": "desc",
            "description": "desc",
            "required": False,
            "paramType": "form",
            "dataType": 'string'
        }, {
            "name": "tags",
            "description": "tags , split by ','",
            "required": False,
            "paramType": "form",
            "dataType": 'string'
        }, {
            "name": "run_type",
            "description": "onetime/periodic",
            "required": False,
            "paramType": "form",
            "dataType": 'string'
        }, {
            "name": "priority",
            "description": "LOW: -1, NORMAL: 0, HIGH: 1, HIGHEST: 2",
            "required": False,
            "paramType": "form",
            "dataType": 'int'
        }, {
            "name": "cron_minutes",
            "description": "@see http://apscheduler.readthedocs.io/en/latest/modules/triggers/cron.html",
            "required": False,
            "paramType": "form",
            "dataType": 'string'
        }, {
            "name": "cron_hour",
            "description": "",
            "required": False,
            "paramType": "form",
            "dataType": 'string'
        }, {
            "name": "cron_day_of_month",
            "description": "",
            "required": False,
            "paramType": "form",
            "dataType": 'string'
        }, {
            "name": "cron_day_of_week",
            "description": "",
            "required": False,
            "paramType": "form",
            "dataType": 'string'
        }, {
            "name": "cron_month",
            "description": "",
            "required": False,
            "paramType": "form",
            "dataType": 'string'
        }, {
            "name": "enabled",
            "description": "-1 / 0, default: 0",
            "required": False,
            "paramType": "form",
            "dataType": 'int'
        }, {
            "name": "status",
            "description": "if set to 'run' will run the job",
            "required": False,
            "paramType": "form",
            "dataType": 'int'
        }

        ])
    def put(self, project_id, job_id):
        post_data = request.form
        if post_data:
            job_instance = JobInstance.query.filter_by(project_id=project_id, id=job_id).first()
            if not job_instance: abort(404)
            job_instance.spider_arguments = post_data.get('spider_arguments') or job_instance.spider_arguments
            job_instance.priority = post_data.get('priority') or job_instance.priority
            job_instance.enabled = post_data.get('enabled', 0)
            job_instance.cron_minutes = post_data.get('cron_minutes') or job_instance.cron_minutes
            job_instance.cron_hour = post_data.get('cron_hour') or job_instance.cron_hour
            job_instance.cron_day_of_month = post_data.get('cron_day_of_month') or job_instance.cron_day_of_month
            job_instance.cron_day_of_week = post_data.get('cron_day_of_week') or job_instance.cron_day_of_week
            job_instance.cron_month = post_data.get('cron_month') or job_instance.cron_month
            job_instance.desc = post_data.get('desc', 0) or job_instance.desc
            job_instance.tags = post_data.get('tags', 0) or job_instance.tags
            db.session.commit()
            if post_data.get('status') == 'run':
                agent.start_spider(job_instance)
            return True


class JobExecutionCtrl(flask_restful.Resource):
    @swagger.operation(
        summary='list job execution status',
        parameters=[{
            "name": "project_id",
            "description": "project id",
            "required": True,
            "paramType": "path",
            "dataType": 'int'
        }])
    def get(self, project_id):
        return JobExecution.list_jobs(project_id)


class JobExecutionDetailCtrl(flask_restful.Resource):
    @swagger.operation(
        summary='stop job',
        notes='',
        parameters=[
            {
                "name": "project_id",
                "description": "project id",
                "required": True,
                "paramType": "path",
                "dataType": 'int'
            },
            {
                "name": "job_exec_id",
                "description": "job_execution_id",
                "required": True,
                "paramType": "path",
                "dataType": 'string'
            }
        ])
    def put(self, project_id, job_exec_id):
        job_execution = JobExecution.query.filter_by(project_id=project_id, id=job_exec_id).first()
        if job_execution:
            agent.cancel_spider(job_execution)
            return True


api.add_resource(ProjectCtrl, "/api/projects")
api.add_resource(SpiderCtrl, "/api/projects/<project_id>/spiders")
api.add_resource(SpiderDetailCtrl, "/api/projects/<project_id>/spiders/<spider_id>")
api.add_resource(JobCtrl, "/api/projects/<project_id>/jobs")
api.add_resource(JobDetailCtrl, "/api/projects/<project_id>/jobs/<job_id>")
api.add_resource(JobExecutionCtrl, "/api/projects/<project_id>/jobexecs")
api.add_resource(JobExecutionDetailCtrl, "/api/projects/<project_id>/jobexecs/<job_exec_id>")

'''
========= Router =========
'''


@app.context_processor
def inject_common():
    return dict(now=datetime.datetime.now(),
                servers=agent.servers)


@app.context_processor
def inject_project():
    project_context = {}
    project = None
    projects = Project.query.all()
    project_context['project_list'] = projects
    if projects:
        project = projects[0]

    project_id = session.get('project_id')
    if isinstance(project_id, int):
        project = Project.query.get(project_id) or project

    if project:
        session['project_id'] = project.id
        project_context['project'] = project
        project_context['spider_list'] = [
            spider_instance.to_dict() for spider_instance in
            SpiderInstance.query.filter_by(project_id=project.id).all()]
    else:
        project_context['project'] = {}
    return project_context


@app.context_processor
def utility_processor():
    def timedelta(end_time, start_time):
        """

        :param end_time:
        :param start_time:
        :param unit: s m h
        :return:
        """
        if not end_time or not start_time:
            return ''
        if type(end_time) == str:
            end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
        if type(start_time) == str:
            start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
        total_seconds = (end_time - start_time).total_seconds()
        return readable_time(total_seconds)

    def readable_time(total_seconds):
        if not total_seconds:
            return '-'
        if total_seconds / 60 == 0:
            return '%s s' % total_seconds
        if total_seconds / 3600 == 0:
            return '%s m' % int(total_seconds / 60)
        return '%s h %s m' % (int(total_seconds / 3600), int((total_seconds % 3600) / 60))

    return dict(timedelta=timedelta, readable_time=readable_time)


@app.route("/")
def index():
    project = Project.query.first()
    if project:
        return redirect("/project/%s/job/dashboard" % project.id, code=302)
    return render_template("index.html")


@app.route("/project/<int:project_id>")
def project_index(project_id):
    Project.query.get_or_404(project_id)
    session['project_id'] = project_id
    return redirect("/project/%s/job/dashboard" % project_id, code=302)


@app.route("/project/<int:project_id>/delete")
def project_delete(project_id):
    project = Project.query.get_or_404(project_id)
    agent.delete_project(project)
    db.session.delete(project)
    db.session.commit()
    return redirect(url_for('index'))


@app.route("/project/<int:project_id>/manage")
def project_manage(project_id):
    Project.query.get_or_404(project_id)
    session['project_id'] = project_id
    return render_template("project_manage.html")


@app.route("/project/<int:project_id>/job/dashboard")
def job_dashboard(project_id):
    Project.query.get_or_404(project_id)
    session['project_id'] = project_id
    return render_template("job_dashboard.html", job_status=JobExecution.list_jobs(project_id))


@app.route("/project/<int:project_id>/job/periodic")
def job_periodic(project_id):
    Project.query.get_or_404(project_id)
    session['project_id'] = project_id
    job_instance_list = [job_instance.to_dict() for job_instance in
                         JobInstance.query.filter_by(run_type="periodic", project_id=project_id).all()]
    return render_template("job_periodic.html",
                           job_instance_list=job_instance_list)


@app.route("/project/<int:project_id>/job/add", methods=['post'])
def job_add(project_id):
    Project.query.get_or_404(project_id)
    job_instance = JobInstance()
    job_instance.spider_name = request.form['spider_name']
    job_instance.project_id = project_id
    job_instance.spider_arguments = request.form['spider_arguments']
    job_instance.priority = request.form.get('priority', 0)
    job_instance.run_type = request.form['run_type']
    # chose daemon manually
    if request.form['daemon'] != 'auto':
        spider_args = []
        if request.form['spider_arguments']:
            spider_args = request.form['spider_arguments'].split(",")
        spider_args.append("daemon={}".format(request.form['daemon']))
        job_instance.spider_arguments = ','.join(spider_args)
    if job_instance.run_type == JobRunType.ONETIME:
        job_instance.enabled = -1
        db.session.add(job_instance)
        db.session.commit()
        agent.start_spider(job_instance)
    if job_instance.run_type == JobRunType.PERIODIC:
        job_instance.cron_minutes = request.form.get('cron_minutes') or '0'
        job_instance.cron_hour = request.form.get('cron_hour') or '*'
        job_instance.cron_day_of_month = request.form.get('cron_day_of_month') or '*'
        job_instance.cron_day_of_week = request.form.get('cron_day_of_week') or '*'
        job_instance.cron_month = request.form.get('cron_month') or '*'
        # set cron exp manually
        if request.form.get('cron_exp'):
            job_instance.cron_minutes, job_instance.cron_hour, job_instance.cron_day_of_month, job_instance.cron_day_of_week, job_instance.cron_month = \
                request.form['cron_exp'].split(' ')
        db.session.add(job_instance)
        db.session.commit()
    return redirect(request.referrer, code=302)


@app.route("/project/<int:project_id>/jobexecs/<int:job_exec_id>/stop")
def job_stop(project_id, job_exec_id):
    job_execution = JobExecution.query.get_or_404(job_exec_id)
    agent.cancel_spider(job_execution)
    return redirect(request.referrer, code=302)


@app.route("/project/jobexecs/<int:job_exec_id>/log")
def job_log(job_exec_id):
    job_execution = JobExecution.query.get_or_404(job_exec_id)
    res = requests.get(agent.log_url(job_execution))
    res.encoding = 'utf8'
    return Response(res.text, content_type='text/plain; charset=utf-8')


@app.route("/project/job/<int:job_instance_id>/run")
def job_run(job_instance_id):
    job_instance = JobInstance.query.get_or_404(job_instance_id)
    agent.start_spider(job_instance)
    return redirect(request.referrer, code=302)


@app.route("/job/<int:job_instance_id>/remove")
def job_remove(job_instance_id):
    job_instance = JobInstance.query.get_or_404(job_instance_id)
    db.session.delete(job_instance)
    db.session.commit()
    return redirect(request.referrer, code=302)


@app.route("/project/<int:project_id>/jobs/remove")
def jobs_remove(project_id):
    for job_instance in JobInstance.query.filter_by(project_id=project_id):
        db.session.delete(job_instance)
    db.session.commit()
    return redirect(request.referrer, code=302)


@app.route("/project/<int:project_id>/job/<int:job_instance_id>/switch")
def job_switch(project_id, job_instance_id):
    job_instance = JobInstance.query.get_or_404(job_instance_id)
    job_instance.enabled = -1 if job_instance.enabled == 0 else 0
    db.session.commit()
    return redirect(request.referrer, code=302)


@app.route("/project/<int:project_id>/spider/dashboard")
def spider_dashboard(project_id):
    Project.query.get_or_404(project_id)
    session['project_id'] = project_id
    last_runtime_query = db.session.query(
        SpiderInstance.spider_name,
        func.Max(JobExecution.date_created).label('last_runtime'),
    ).outerjoin(JobInstance, JobInstance.spider_name == SpiderInstance.spider_name)\
        .outerjoin(JobExecution).filter(SpiderInstance.project_id == project_id)\
        .group_by(SpiderInstance.id)

    last_runtime = dict(
        (spider_name, last_runtime) for spider_name, last_runtime in last_runtime_query
    )

    avg_runtime_query = db.session.query(
        SpiderInstance.spider_name,
        func.Avg(JobExecution.end_time - JobExecution.start_time).label('avg_runtime'),
    ).outerjoin(JobInstance, JobInstance.spider_name == SpiderInstance.spider_name)\
        .outerjoin(JobExecution).filter(SpiderInstance.project_id == project_id)\
        .filter(JobExecution.end_time != None)\
        .group_by(SpiderInstance.id)

    avg_runtime = dict(
        (spider_name, avg_runtime) for spider_name, avg_runtime in avg_runtime_query
    )

    spiders = []
    for spider in SpiderInstance.query.filter(SpiderInstance.project_id == project_id).all():
        spider.last_runtime = last_runtime.get(spider.spider_name)
        spider.avg_runtime = avg_runtime.get(spider.spider_name)
        if spider.avg_runtime is not None:
            spider.avg_runtime = spider.avg_runtime.total_seconds()
        spiders.append(spider)
    return render_template("spider_dashboard.html", spiders=spiders)


@app.route("/project/<int:project_id>/spider/deploy")
def spider_deploy(project_id):
    Project.query.get_or_404(project_id)
    session['project_id'] = project_id
    return render_template("spider_deploy.html")


@app.route("/project/<int:project_id>/spider/upload", methods=['post'])
def spider_egg_upload(project_id):
    project = Project.query.get(project_id)
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.referrer)
    file = request.files['file']
    # if user does not select file, browser also
    # submit a empty part without filename
    if file.filename == '':
        flash('No selected file')
        return redirect(request.referrer)
    if file:
        filename = secure_filename(file.filename)
        dst = os.path.join(tempfile.gettempdir(), filename)
        file.save(dst)
        agent.deploy(project, dst)
        flash('deploy success!')
    return redirect(request.referrer)


@app.route("/project/<int:project_id>/project/stats")
def project_stats(project_id):
    Project.query.get_or_404(project_id)
    session['project_id'] = project_id
    run_stats = JobExecution.list_run_stats_by_hours(project_id)
    return render_template("project_stats.html", run_stats=run_stats)


@app.route("/project/<int:project_id>/server/stats")
def service_stats(project_id):
    Project.query.get_or_404(project_id)
    session['project_id'] = project_id
    run_stats = JobExecution.list_run_stats_by_hours(project_id)
    return render_template("server_stats.html", run_stats=run_stats)
