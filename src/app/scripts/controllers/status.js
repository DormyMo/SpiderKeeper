'use strict';

/**
 * @ngdoc function
 * @name spiderKeeperApp.controller:StatusCtrl
 * @description
 * # StatusCtrl
 * Controller of the spiderKeeperApp
 */
angular.module('spiderKeeperApp')
  .controller('StatusCtrl', function ($rootScope) {
    $rootScope.status = 'status'
  });
