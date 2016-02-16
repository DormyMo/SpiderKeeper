'use strict';

/**
 * @ngdoc function
 * @name spiderKeeperApp.controller:DashschdulerCtrl
 * @description
 * # DashschdulerCtrl
 * Controller of the spiderKeeperApp
 */
angular.module('spiderKeeperApp')
  .controller('DashschdulerCtrl', function ($scope,$rootScope,SKService,$interval) {
    $scope.getSchedulers = function(){
      SKService.getScheduler($rootScope.currProject).then(function(data){
        console.log(data)
        $scope.schedulers = data.data.data;
      })
    }

    $scope.getSchedulers() //init

    //$interval($scope.getSchedulers,30000);//refresh date

    $scope.btnRemoveScheduleClick = function (schedule) {
      SKService.removeSchedule(schedule.id);

    }

  });
