# -*- coding: utf-8 -*-
import flask_restful
from flask_restful_swagger import swagger
from flask import request, abort
from flask_restful import Api
import SpiderKeeper
from SpiderKeeper.app.proxy import agent
from SpiderKeeper.app.extensions.sqlalchemy import db
from SpiderKeeper.app.blueprints.dashboard.model import JobInstance, Project, JobExecution, \
    SpiderInstance, JobRunType


api = swagger.docs(
    Api(), apiVersion=SpiderKeeper.__version__,
    api_spec_url="/api", description='SpiderKeeper'
)


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

api.add_resource(ProjectCtrl, "/api/projects")


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

api.add_resource(SpiderCtrl, "/api/projects/<project_id>/spiders")


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

api.add_resource(SpiderDetailCtrl, "/api/projects/<project_id>/spiders/<spider_id>")


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

api.add_resource(JobCtrl, "/api/projects/<project_id>/jobs")


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

api.add_resource(JobDetailCtrl, "/api/projects/<project_id>/jobs/<job_id>")


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

api.add_resource(JobExecutionCtrl, "/api/projects/<project_id>/jobexecs")


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

api.add_resource(JobExecutionDetailCtrl, "/api/projects/<project_id>/jobexecs/<job_exec_id>")
