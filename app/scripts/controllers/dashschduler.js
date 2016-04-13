'use strict';

/**
 * @ngdoc function
 * @name spiderKeeperApp.controller:DashschdulerCtrl
 * @description
 * # DashschdulerCtrl
 * Controller of the spiderKeeperApp
 */
angular.module('spiderKeeperApp')
    .controller('DashschdulerCtrl', ['$scope', '$rootScope', 'daemonService', '$interval', function ($scope, $rootScope, daemonService, $interval) {

        $scope.getSchedulers = function () {
            daemonService.getScheduler($rootScope.currProject).then(function (data) {
                $scope.schedulers = data.data.data;
            })
        }

        $scope.getSchedulers() //init

        $scope.btnRemoveScheduleClick = function (schedule) {
            daemonService.removeSchedule(schedule.id);

        }

    }]);
