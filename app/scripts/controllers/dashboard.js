'use strict';

/**
 * @ngdoc function
 * @name spiderKeeperApp.controller:DashboardCtrl
 * @description
 * # DashboardCtrl
 * Controller of the spiderKeeperApp
 */
angular.module('spiderKeeperApp')
    .controller('DashboardCtrl', ['$scope', '$rootScope', '$routeParams', '$location', '$interval', 'daemonService', function ($scope, $rootScope, $routeParams, $location, $interval, daemonService) {

        $rootScope.status = 'dashboard'
        $scope.daemons = daemonService.listDaemons()
        $rootScope.currDaemon = [$scope.daemons[0].name]

        daemonService.listProjects($rootScope.currDaemon).then(function (data) {
            $scope.projectNames = data.data.projects;
            $rootScope.currProject = $routeParams.project || $scope.projectNames[0]

        })

        $scope.menus = [
            {name: 'Spiders', page: "views/dash_spider.html"},
            {name: 'Jobs', page: "views/dash_job.html"},
            {name: 'Collections'},
            {name: 'Schedule', page: "views/dash_scheduler.html"}]

        $scope.currMenuName = $routeParams.menu || $scope.menus[0].name

        for (var i in $scope.menus) {
            if ($scope.menus[i].name == $scope.currMenuName) {
                $scope.subPage = $scope.menus[i].page
                break
            }
        }

        $scope.getDaemonStatus = function () {
            daemonService.daemonStatus($rootScope.currDaemon).then(function (data) {
                $rootScope.currDaemonStatus = data.data.data[0];
                $scope.menus[1].badge = $rootScope.currDaemonStatus.running;
            })
        }

        $scope.getDaemonStatus() //init

        $interval($scope.getDaemonStatus, 1000);//refresh data


        $scope.menuClick = function (menu) {
            $location.search({'menu': menu.name})
        }

        $scope.daemonChange = function (daemon) {
            $rootScope.currDaemon = [daemon]
        }

    }]);
