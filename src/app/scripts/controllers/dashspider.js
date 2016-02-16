'use strict';

/**
 * @ngdoc function
 * @name spiderKeeperApp.controller:DashspiderCtrl
 * @description
 * # DashspiderCtrl
 * Controller of the spiderKeeperApp
 */
angular.module('spiderKeeperApp')
  .controller('DashspiderCtrl', function ($scope,$rootScope,scrapydApi,$routeParams,$location,SKService) {


    scrapydApi.listProjects().then(function(data){
      $scope.projectNames = data.data;

    })
    $scope.spiders={}
    scrapydApi.listSpiders($rootScope.currProject||'CuteSpider').then(function(data){
      console.log(data)
      $scope.spideNames = data.data.spiders;
      for (var i in $scope.spideNames)
      {
        $scope.spiders[$scope.spideNames[i]]={'name':$scope.spideNames[i],'status':'pending',params:""}
      }

    })

    $scope.btnRunClick = function(spider){
      console.log(spider)
      scrapydApi.schedule($scope.currProject,spider.name,spider.params).then(function (data) {
        $location.search({'menu':'Jobs'})
        console.log(data)
      })

    }

    $scope.btnScheduleClick = function(spider){
      $scope.scheduleSpider = spider
      $scope.scheduleSpider.startTime = moment().format('YYYY-MM-DD HH:mm:ss')
      $scope.scheduleSpider.times = 1
      $scope.scheduleSpider.interval = 0
      $('#modelSchedule').show()

    }

    $scope.btnScheduleSubmit = function () {
      SKService.schedule($rootScope.currProject,
        $scope.scheduleSpider.name,
        $scope.scheduleSpider.params,
        $scope.scheduleSpider.startTime,
        $scope.scheduleSpider.interval,
        $scope.scheduleSpider.times).then(function(data){
        console.log(data)
        $('#modelSchedule').hide()
        $location.search({'menu':'Schedule'})
      })


    }


  });
