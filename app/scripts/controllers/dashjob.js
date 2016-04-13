'use strict';

/**
 * @ngdoc function
 * @name spiderKeeperApp.controller:DashjobCtrl
 * @description
 * # DashjobCtrl
 * Controller of the spiderKeeperApp
 */
angular.module('spiderKeeperApp')
    .controller('DashjobCtrl', ['$scope', '$rootScope', 'daemonService', '$routeParams', '$interval', function ($scope, $rootScope, daemonService, $routeParams, $interval) {
        function load() {
            $scope.jobStates = ['Pending', 'Running', 'Finished']
            $scope.jobState = 'running'
            $scope.jobs = {}
            $scope.listJobs = function (status) {
                daemonService.listJobs($rootScope.currProject, $rootScope.currDaemon, status).then(function (data) {
                    $scope.jobs[status] = []
                    for (var i in $rootScope.currDaemon) {
                        var jobList = data.data.data[$rootScope.currDaemon[i]][status]
                        for (var j in jobList) {
                            jobList[j]['daemon'] = $rootScope.currDaemon[i]
                            $scope.jobs[status].push(jobList[j]);
                        }
                    }
                })
            }
            $scope.listJobs('running')
            $interval(function () {
                $scope.listJobs('pending')
            }, 20000);//refresh data
            $interval(function () {
                $scope.listJobs('running')
            }, 10000);//refresh data

            //$interval(function(){$scope.listJobs('finished')},50000);//refresh data


            $scope.btnJobFinishedClick = function () {
                $scope.listJobs('finished')
            }


            $scope.btnCancelClick = function (item) {
                daemonService.cancel($rootScope.currProject, item.id, $rootScope.currDaemon).then(function (data) {
                })
            }

            $scope.btnLogClick = function (item) {
                $scope.logUrl = daemonService.getLogSceUrl($rootScope.currProject, item.spider, item.id, item.daemon)
                $('#modelLog').show()
            }
        }

        load()

        $rootScope.$watch('currDaemon', function (newVal, oldVal) {
            load()
        })

        $scope.jobShowType = function (e) {
            if ($rootScope.currDaemon.length > 1) {
                $rootScope.currDaemon = [daemonService.getDaemonNames()[0]]
            }
            else {
                $rootScope.currDaemon = daemonService.getDaemonNames()
            }
        }

    }]);
