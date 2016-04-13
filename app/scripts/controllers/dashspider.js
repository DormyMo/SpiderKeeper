'use strict';

/**
 * @ngdoc function
 * @name spiderKeeperApp.controller:DashspiderCtrl
 * @description
 * # DashspiderCtrl
 * Controller of the spiderKeeperApp
 */
angular.module('spiderKeeperApp')
    .controller('DashspiderCtrl', ['$scope', '$rootScope', 'daemonService', '$routeParams', '$location', 'ngNotify', function ($scope, $rootScope, daemonService, $routeParams, $location, ngNotify) {
        function load() {
            $scope.spiders = {}
            $scope.runType = 'run'
            $scope.daemons = daemonService.listDaemons()
            $rootScope.$watch('currProject', function (newVal, oldVal) {
                if (newVal) {
                    daemonService.listSpiders($rootScope.currProject).then(function (data) {
                        $scope.spideNames = data.data.spiders;
                        for (var i in $scope.spideNames) {
                            $scope.spiders[$scope.spideNames[i]] = {
                                'name': $scope.spideNames[i],
                                'status': 'pending',
                                params: ""
                            }
                        }

                    })
                }
            })


            $scope.btnRunClick = function (spider) {
                $scope.runType = 'run'
                $scope.scheduleSpider = spider
                $('#modelSchedule').show()

            }

            $scope.btnScheduleClick = function (spider) {
                $scope.runType = 'schedule'
                $scope.scheduleSpider = spider
                $scope.scheduleSpider.startTime = moment().format('YYYY-MM-DD HH:mm:ss')
                $scope.scheduleSpider.times = 1
                $scope.scheduleSpider.interval = 0
                $('#modelSchedule').show()

            }

            function getTips(spiderName, data) {
                var content = spiderName + 'has running on ['
                for (var i in data) {
                    content += data[i].daemon + '(' + (data[i].jobid || data[i].status) + ') , '
                }
                content += ']'
                return content
            }

            $scope.btnScheduleSubmit = function () {
                var sel_daemons = []
                for (var i in $scope.daemons) {
                    if ($scope.daemons[i].selected) {
                        sel_daemons.push($scope.daemons[i].name)
                    }

                }
                if ($scope.runType == 'run') {

                    daemonService.schedule($scope.currProject, $scope.scheduleSpider.name, $scope.scheduleSpider.params, sel_daemons).then(function (data) {
                        data = data.data.data
                        var content = $scope.scheduleSpider.name + ' has running on ['
                        for (var i in data) {
                            content += data[i].daemon + '(' + (data[i].jobid || data[i].status) + ') , '
                        }
                        content += ']'
                        ngNotify.set(content);
                        $location.search({'menu': 'Jobs'})
                    })
                }
                else {
                    daemonService.addSchedule($rootScope.currProject,
                        $scope.scheduleSpider.name,
                        $scope.scheduleSpider.params,
                        $scope.scheduleSpider.startTime,
                        $scope.scheduleSpider.interval,
                        $scope.scheduleSpider.times,
                        sel_daemons).then(function (data) {

                        if (data.data.status == 'ok') {

                            ngNotify.set($scope.scheduleSpider.name + ' has added to schedule');
                            $location.search({'menu': 'Schedule'})
                        }
                        else {

                            ngNotify.set($scope.scheduleSpider.name + ' adding to schedule error', 'error');
                        }


                    })
                }
                $('#modelSchedule').hide()


            }
        }

        load()

        $rootScope.$watch('currDaemon', function (newVal, oldVal) {
            load()
        })


    }]);
