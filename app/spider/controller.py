import flask_restful
from flask import Blueprint, request
from flask.ext.restful_swagger import swagger

from app import db, api, agent
from app.spider.model import JobInstance, Project

api_spider_bp = Blueprint('spider', __name__)


class ProjectCtrl(flask_restful.Resource):
    @swagger.operation(
        summary='list projects',
        parameters=[])
    def get(self):
        return agent.get_project_list()


class SpiderCtrl(flask_restful.Resource):
    @swagger.operation(
        summary='list spiders',
        parameters=[{
            "name": "project_id",
            "description": "project id",
            "required": True,
            "paramType": "path",
            "dataType": 'string'
        }])
    def get(self, project_id):
        project = Project.find_project_by_id(project_id)
        return agent.get_spider_list(project) if project else []


class JobCtrl(flask_restful.Resource):
    @swagger.operation(
        summary='list job instance',
        parameters=[{
            "name": "project_id",
            "description": "project id",
            "required": True,
            "paramType": "path",
            "dataType": 'string'
        }])
    def get(self, project_id):
        return [job_instance.to_dict() for job_instance in
                JobInstance.query.filter_by(run_type="periodic", project_id=project_id).all()]

    @swagger.operation(
        summary='add job instance',
        notes="json keys: spider_name,tags,spider_arguments,priority,desc,cron_minutes,cron_hour,cron_day_of_month,cron_day_of_week,cron_month,enabled,run_type",
        parameters=[{
            "name": "project_id",
            "description": "project id",
            "required": True,
            "paramType": "path",
            "dataType": 'string'
        }])
    def post(self, project_id):
        post_data = request.json
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
        summary='update job info',
        notes="json keys: tags,spider_arguments,priority,desc,cron_minutes,cron_hour,cron_day_of_month,cron_day_of_week,cron_month,enabled",
        parameters=[{
            "name": "job_id",
            "description": "job instance id",
            "required": True,
            "paramType": "path",
            "dataType": 'string'
        }])
    def post(self, project_id, job_id):
        post_data = request.json
        if post_data:
            job_instance = JobInstance.query.filter_by(project_id=project_id, id=job_id).first()
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
            db.session.commit(job_instance)
            return True


class JobExecutionCtrl(flask_restful.Resource):
    @swagger.operation(
        summary='list job execution status',
        parameters=[{
            "name": "project_id",
            "description": "project id",
            "required": True,
            "paramType": "path",
            "dataType": 'string'
        }])
    def get(self, project_id):
        project = Project.find_project_by_id(project_id)
        return agent.get_job_status(project)


class JobExecutionOperationCtrl(flask_restful.Resource):
    @swagger.operation(
        summary='operate job',
        notes='args: operation: [run/stop]',
        parameters=[
            {
                "name": "project_id",
                "description": "project id",
                "required": True,
                "paramType": "path",
                "dataType": 'string'
            },
            {
                "name": "job_exec_id",
                "description": "job_execution_id",
                "required": True,
                "paramType": "path",
                "dataType": 'string'
            }
        ])
    def get(self, project_id, job_id):
        operation = request.args.get("operation")
        job_instance = JobInstance.query.filter_by(project_id=project_id, id=job_id).first()
        if operation and job_instance:
            if operation == 'run':
                agent.start_spider(job_instance)
                return True
            if operation == 'stop':
                agent.cancel_spider(job_instance)
                return True


api.add_resource(ProjectCtrl, "/projects")
api.add_resource(SpiderCtrl, "/projects/<project_id>/spiders")
api.add_resource(JobCtrl, "/projects/<project_id>/jobs")
api.add_resource(JobDetailCtrl, "/projects/<project_id>/jobs/<job_id>")
api.add_resource(JobExecutionCtrl, "/projects/<project_id>/jobexecs")
api.add_resource(JobExecutionOperationCtrl, "/projects/<project_id>/jobexecs/<job_exec_id>")

pass
