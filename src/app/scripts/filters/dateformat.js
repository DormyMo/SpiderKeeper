'use strict';

/**
 * @ngdoc filter
 * @name spiderKeeperApp.filter:dateformat
 * @function
 * @description
 * # dateformat
 * Filter in the spiderKeeperApp.
 */
angular.module('spiderKeeperApp')
  .filter('dateformat', function () {
    return function (input) {
      return moment(input).format('YYYY-MM-DD HH:mm:ss');
    };
  });
