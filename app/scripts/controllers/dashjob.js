'use strict';

/**
 * @ngdoc function
 * @name spiderKeeperApp.controller:DashjobCtrl
 * @description
 * # DashjobCtrl
 * Controller of the spiderKeeperApp
 */
angular.module('spiderKeeperApp')
  .controller('DashjobCtrl', function ($scope,$rootScope,scrapydApi,$routeParams,$interval,$sce
  ) {


    $scope.jobStates=['Pending','Running','Finished']
    $scope.jobState = 'running'
    $scope.listJobs = function() {
      scrapydApi.listJobs($rootScope.currProject).then(function (data) {

        $scope.jobs = data.data;
        //console.log($scope.jobs)
        $scope.jobData = $scope.jobs!=undefined?$scope.jobs[$scope.jobState]:{}

      })
    }
    $scope.listJobs()//init jobs
    $scope.jobData = $scope.jobs!=undefined?$scope.jobs[$scope.jobState]:{} //init job data
    $scope.jobFinished =  $scope.jobs!=undefined?$scope.jobs.finished:{} //init finished job data

    $interval($scope.listJobs,3000);//refresh data


    $scope.btnJobFinishedClick = function()
    {
      $scope.jobFinished = $scope.jobs.finished
    }

    $scope.tabClick = function(state)
    {
      $scope.jobState = state.toLowerCase()
      $scope.jobData = $scope.jobs[state.toLowerCase()]
    }

    $scope.btnCancelClick = function(item)
    {
      scrapydApi.cancel($rootScope.currProject,item.id).then(function(data){
        console.log(data)
      })
    }

    $scope.btnLogClick = function(item)
    {
      console.log(item)
      $scope.logUrl = scrapydApi.getLogSceUrl($rootScope.currProject,item.spider,item.id)
      $('#modelLog').show()
    }
  });
