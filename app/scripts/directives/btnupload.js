'use strict';

/**
 * @ngdoc directive
 * @name spiderKeeperApp.directive:btnUpload
 * @description
 * # btnUpload
 */
angular.module('spiderKeeperApp')
  .directive('btnUpload', function () {
    return {
      template: '<div ng-style="position:fixed;right: 30px;bottom: 30px;"  class="btn btn-info btn-fab" data-toggle="tooltip" data-placement="top" title="deploy project" data-original-title="deploy project" ng -click="click()"><i class="material-icons"  >add<input id="file" type="file" style="display:none;" /></i></div>',
      restrict: 'AE',
      scope: true,
      link: function postLink(scope, element, attrs) {
        $scope.click = function(){
          element.find('#file').click()
        }

      }
    };
  });
