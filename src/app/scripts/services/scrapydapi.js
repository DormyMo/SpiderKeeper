'use strict';

/**
 * @ngdoc service
 * @name spiderKeeperApp.scrapydApi
 * @description
 * # scrapydApi
 * Service in the spiderKeeperApp.
 */
var scrapydApiEndpoint = "http://your.end.point/scrapyd"
angular.module('spiderKeeperApp')
  .service('scrapydApi', function ($http,$sce) {
    return ({
      scrapydApiUrl:scrapydApiEndpoint,
      scrapydScheduleApi:$sce.trustAsResourceUrl(scrapydApiEndpoint+"/schedule.json"),
      listSpiders:listSpiders,
      listJobs:listJobs,
      listProjects:listProjects,
      daemonStatus:daemonStatus,
      schedule:schedule,
      cancel:cancel,
      getLogSceUrl:getLogSceUrl
    })

    function listSpiders(projectName) {


      var request = $http({
        method: "get",
        url: scrapydApiEndpoint+"/listspiders.json",
        params: {
          project: projectName
        }
      });

      return request
    }

    function listJobs(projectName) {

      var request = $http({
        method: "get",
        url: scrapydApiEndpoint+"/listjobs.json",
        params: {
          project: projectName
        }
      });

      return request
    }

    function listProjects() {

      var request = $http({
        method: "get",
        url: scrapydApiEndpoint+"/listprojects.json"
      });

      return request
    }

    function daemonStatus() {

      var request = $http({
        method: "get",
        url: scrapydApiEndpoint+"/daemonstatus.json"
      });

      return request
    }

    function schedule(project,spider,paramStr)
    {
      var params ={
        "project":project,
        "spider":spider};
      var paramArray = paramStr.split(',');
      for(var i = 0;i<paramArray.length;i++)
      {
        var kv = paramArray[i].split('=');
        params[kv[0]] = kv[1];
      }
      var request = $http({
        method: "post",
        url: scrapydApiEndpoint+"/schedule.json",
        params:params
      });

      return request
    }

    function cancel(project,jobId)
    {
      var request = $http({
        method: "post",
        url: scrapydApiEndpoint+"/cancel.json",
        params:{"project":project,
          "job":jobId}
      });

      return request
    }

    function getLogSceUrl(project,spider,jobId)
    {
      return $sce.trustAsResourceUrl(scrapydApiEndpoint+"/logs/"+project+"/"+spider+"/"+jobId+".log");
    }
  });
