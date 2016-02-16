'use strict';

/**
 * @ngdoc function
 * @name spiderKeeperApp.controller:DashboardCtrl
 * @description
 * # DashboardCtrl
 * Controller of the spiderKeeperApp
 */
angular.module('spiderKeeperApp')
  .controller('DashboardCtrl', function ($scope,$rootScope,$routeParams,$location,$interval,scrapydApi) {

    $rootScope.status = 'dashboard'
    //$rootScope.scrapydApiUrl = scrapydApi.scrapydApiUrl;




    $scope.menus=[
      {name:'Spiders',page:"views/dash_spider.html"},
      {name:'Jobs',page:"views/dash_job.html"},
      {name:'Collections'},
      {name:'Schedule',page:"views/dash_scheduler.html"}]
    $scope.currMenuName=$routeParams.menu||$scope.menus[0].name

    for (var i in $scope.menus)
    {
      if ($scope.menus[i].name == $scope.currMenuName)
      {
        $scope.subPage = $scope.menus[i].page
        break
      }
    }

    $scope.getDaemonStatus = function(){
      scrapydApi.daemonStatus().then(function(data){
        $rootScope.daemonStatus = data.data;
        $scope.menus[1].badge = $rootScope.daemonStatus.running;
      })
    }
    $scope.getDaemonStatus() //init
    $interval($scope.getDaemonStatus,1000);//refresh data

    scrapydApi.listProjects().then(function(data){
      $scope.projectNames = data.data.projects;
      $rootScope.currProject =$routeParams.project || $scope.projectNames[0]

    })

    $scope.menuClick = function(menu)
    {
      $location.search({'menu':menu.name})
    }

  });
