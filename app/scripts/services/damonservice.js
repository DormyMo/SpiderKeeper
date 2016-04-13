'use strict';

/**
 * @ngdoc service
 * @name spiderKeeperApp.scrapydApi
 * @description
 * # scrapydApi
 * Service in the spiderKeeperApp.
 */
//var daemonServicePrefix = "http://localhost:6800"
angular.module('spiderKeeperApp')
    .service('daemonService', ['APP_CONFIG', '$http', '$sce', function (APP_CONFIG, $http, $sce) {
        console.log('APP_CONFIG is: ' + JSON.stringify(APP_CONFIG));
        var daemonServicePrefix = APP_CONFIG.server
        return ({
            listDaemons: listDaemons,
            getDaemonNames: getDaemonNames,
            listSpiders: listSpiders,
            listJobs: listJobs,
            listProjects: listProjects,
            daemonStatus: daemonStatus,
            schedule: schedule,
            cancel: cancel,
            getLogSceUrl: getLogSceUrl,
            addSchedule: addSchedule,
            getScheduler: getScheduler,
            removeSchedule: removeSchedule
        })

        function listDaemons() {
            return APP_CONFIG.scrapyd
        }

        function getDaemonNames() {
            var daemons = []
            for (var i in APP_CONFIG.scrapyd) {
                daemons.push(APP_CONFIG.scrapyd[i]['name'])
            }
            return daemons
        }

        function listSpiders(projectName) {


            var request = $http({
                method: "get",
                url: daemonServicePrefix + "/spider/list/",
                params: {
                    project: projectName
                }
            });

            return request
        }

        function listJobs(project, daemons, status) {
            status = status || 'all'
            var request = $http({
                method: "get",
                url: daemonServicePrefix + "/job/list/" + status + "/",
                params: {
                    'project': project,
                    'daemons': daemons.join(',')
                }
            });

            return request
        }

        function listProjects() {

            var request = $http({
                method: "get",
                url: daemonServicePrefix + "/project/list/"
            });

            return request
        }

        function daemonStatus(daemons) {

            var request = $http({
                method: "get",
                url: daemonServicePrefix + "/daemon/status/",
                params: {
                    'daemons': daemons.join(',')
                }
            });

            return request
        }

        function schedule(project, spider, paramStr, daemons) {
            var params = {
                'project': project,
                'spider': spider,
                'daemons': daemons.join(',')
            };
            var paramArray = paramStr.split(',');
            for (var i = 0; i < paramArray.length; i++) {
                var kv = paramArray[i].split('=');
                params[kv[0]] = kv[1];
            }
            var request = $http({
                method: "get",
                url: daemonServicePrefix + "/spider/start/",
                params: params
            });

            return request
        }

        function cancel(project, jobId, daemons) {
            var request = $http({
                method: "get",
                url: daemonServicePrefix + "/schedule/cancel/",
                params: {
                    "project": project,
                    "job": jobId,
                    "daemons": daemons.join(',')
                }
            });

            return request
        }

        function getLogSceUrl(project, spider, jobId, daemons) {
            return $sce.trustAsResourceUrl(daemonServicePrefix + "/log/?project=" + project + "&spider=" + spider + "&jobId=" + jobId + "&daemons=" + daemons.join(','));
        }


        function getScheduler(project) {
            var request = $http({
                method: "get",
                url: daemonServicePrefix + "/schedule/list/",
                params: {
                    'project': project
                }
            });

            return request
        }

        function addSchedule(project, spider, params, startTime, interval, times, daemons) {
            var request = $http({
                method: "get",
                url: daemonServicePrefix + "/schedule/add/",
                params: {
                    'project': project,
                    'spider': spider,
                    'params': params,
                    'startTime': startTime,
                    'interval': interval,
                    'times': times,
                    'daemons': daemons.join(',')
                }
            });

            return request
        }

        function removeSchedule(id) {
            var request = $http({
                method: "get",
                url: daemonServicePrefix + "/schedule/del/",
                params: {
                    'id': id
                }
            });

            return request
        }
    }]);
