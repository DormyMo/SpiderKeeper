import datetime
import os
import tempfile


import requests
from flask import Blueprint, request, Response
from flask import url_for
from flask import flash
from flask import redirect
from flask import render_template
from flask import session
from sqlalchemy import func
from werkzeug.utils import secure_filename

from SpiderKeeper.app.proxy import agent
from SpiderKeeper.app.extensions.sqlalchemy import db
from SpiderKeeper.app.blueprints.dashboard.model import JobInstance, Project, JobExecution, \
    SpiderInstance, JobRunType

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.context_processor
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


@dashboard_bp.route("/")
def index():
    project = Project.query.first()
    if project:
        return redirect(url_for('dashboard.job_dashboard', project_id=project.id))
    return render_template("index.html")


@dashboard_bp.route("/project/<int:project_id>")
def project_index(project_id):
    Project.query.get_or_404(project_id)
    session['project_id'] = project_id
    return redirect(url_for('dashboard.job_dashboard', project_id=project_id))


@dashboard_bp.route("/project/<int:project_id>/delete")
def project_delete(project_id):
    project = Project.query.get_or_404(project_id)
    agent.delete_project(project)
    db.session.delete(project)
    db.session.commit()
    return redirect(url_for('dashboard.index'))


@dashboard_bp.route("/project/<int:project_id>/manage")
def project_manage(project_id):
    Project.query.get_or_404(project_id)
    session['project_id'] = project_id
    return render_template("project_manage.html")


@dashboard_bp.route("/project/<int:project_id>/job/dashboard")
def job_dashboard(project_id):
    Project.query.get_or_404(project_id)
    session['project_id'] = project_id
    return render_template("job_dashboard.html", job_status=JobExecution.list_jobs(project_id))


@dashboard_bp.route("/project/<int:project_id>/job/periodic")
def job_periodic(project_id):
    Project.query.get_or_404(project_id)
    session['project_id'] = project_id
    job_instance_list = [job_instance.to_dict() for job_instance in
                         JobInstance.query.filter_by(run_type="periodic", project_id=project_id).all()]
    return render_template("job_periodic.html",
                           job_instance_list=job_instance_list)


@dashboard_bp.route("/project/<int:project_id>/job/add", methods=['post'])
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


@dashboard_bp.route("/project/<int:project_id>/jobexecs/<int:job_exec_id>/stop")
def job_stop(project_id, job_exec_id):
    job_execution = JobExecution.query.get_or_404(job_exec_id)
    agent.cancel_spider(job_execution)
    return redirect(request.referrer, code=302)


@dashboard_bp.route("/project/jobexecs/<int:job_exec_id>/log")
def job_log(job_exec_id):
    job_execution = JobExecution.query.get_or_404(job_exec_id)
    res = requests.get(agent.log_url(job_execution))
    res.encoding = 'utf8'
    return Response(res.text, content_type='text/plain; charset=utf-8')


@dashboard_bp.route("/project/job/<int:job_instance_id>/run")
def job_run(job_instance_id):
    job_instance = JobInstance.query.get_or_404(job_instance_id)
    agent.start_spider(job_instance)
    return redirect(request.referrer, code=302)


@dashboard_bp.route("/job/<int:job_instance_id>/remove")
def job_remove(job_instance_id):
    job_instance = JobInstance.query.get_or_404(job_instance_id)
    db.session.delete(job_instance)
    db.session.commit()
    return redirect(request.referrer, code=302)


@dashboard_bp.route("/project/<int:project_id>/jobs/remove")
def jobs_remove(project_id):
    for job_instance in JobInstance.query.filter_by(project_id=project_id):
        db.session.delete(job_instance)
    db.session.commit()
    return redirect(request.referrer, code=302)


@dashboard_bp.route("/project/<int:project_id>/job/<int:job_instance_id>/switch")
def job_switch(project_id, job_instance_id):
    job_instance = JobInstance.query.get_or_404(job_instance_id)
    job_instance.enabled = -1 if job_instance.enabled == 0 else 0
    db.session.commit()
    return redirect(request.referrer, code=302)


@dashboard_bp.route("/project/<int:project_id>/spider/dashboard")
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


@dashboard_bp.route("/project/<int:project_id>/spider/deploy")
def spider_deploy(project_id):
    Project.query.get_or_404(project_id)
    session['project_id'] = project_id
    return render_template("spider_deploy.html")


@dashboard_bp.route("/project/<int:project_id>/spider/upload", methods=['post'])
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


@dashboard_bp.route("/project/<int:project_id>/project/stats")
def project_stats(project_id):
    Project.query.get_or_404(project_id)
    session['project_id'] = project_id
    run_stats = JobExecution.list_run_stats_by_hours(project_id)
    return render_template("project_stats.html", run_stats=run_stats)


@dashboard_bp.route("/project/<int:project_id>/server/stats")
def service_stats(project_id):
    Project.query.get_or_404(project_id)
    session['project_id'] = project_id
    run_stats = JobExecution.list_run_stats_by_hours(project_id)
    return render_template("server_stats.html", run_stats=run_stats)
