'use strict';

/**
 * @ngdoc service
 * @name spiderKeeperApp.SKService
 * @description
 * # SKService
 * Service in the spiderKeeperApp.
 */
var serviceApiEndpoint = "http://your.end.point.com"
angular.module('spiderKeeperApp')
  .service('SKService', function ($http) {
    return ({
      SKServiceApiUrl:serviceApiEndpoint,
      schedule:schedule,
      getScheduler:getScheduler,
      removeSchedule:removeSchedule
    })

    function getScheduler(project){
      var request = $http({
        method: "get",
        url: serviceApiEndpoint+"/getScheduler",
        params:{
          'project':project
        }
      });

      return request
    }

    function schedule(project,spider,params,startTime,interval,times){
      console.log(spider)
      var request = $http({
        method: "get",
        url: serviceApiEndpoint+"/schedule",
        params:{
          'project':project,
          'spider':spider,
          'params':params,
          'startTime':startTime,
          'interval':interval,
          'times':times
        }
      });

      return request
    }

    function removeSchedule(id){
      var request = $http({
        method: "get",
        url: serviceApiEndpoint+"/removeSchedule",
        params:{
          'id':id
        }
      });

      return request
    }
  });
