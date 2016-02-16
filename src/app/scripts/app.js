'use strict';

/**
 * @ngdoc overview
 * @name spiderKeeperApp
 * @description
 * # spiderKeeperApp
 *
 * Main module of the application.
 */
angular
  .module('spiderKeeperApp', [
    'ngAnimate',
    'ngCookies',
    'ngResource',
    'ngRoute',
    'ngSanitize',
    'ngTouch',
    'initMaterial'
  ])
  .controller(function($rootScope){
    $rootScope.status = 'dashboard'
  })
  .config(function ($routeProvider) {
    $routeProvider
      .when('/about', {
        templateUrl: 'views/about.html',
        controller: 'AboutCtrl',
        controllerAs: 'about'
      })
      .when('/dashboard', {
        templateUrl: 'views/dashboard.html',
        controller: 'DashboardCtrl',
        controllerAs: 'dashboard'
      })
      .when('/status', {
        templateUrl: 'views/status.html',
        controller: 'StatusCtrl',
        controllerAs: 'status'
      })
      .otherwise({
        redirectTo: '/dashboard'
      });
  });
