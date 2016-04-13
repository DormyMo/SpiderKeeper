'use strict';

/**
 * @ngdoc overview
 * @name spiderKeeperApp
 * @description
 * # spiderKeeperApp
 *
 * Main module of the application.
 */
angular.module('spiderKeeperApp', [
        'ngAnimate',
        'ngCookies',
        'ngResource',
        'ngRoute',
        'ngSanitize',
        'ngTouch',
        'initMaterial',
        'ngNotify'
    ])
    .controller(['$rootScope', function ($rootScope) {
        $rootScope.status = 'dashboard'
    }])
    .config(['$routeProvider', function ($routeProvider) {

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
    }]);


deferredBootstrapper.bootstrap({
    element: document.body,
    module: 'spiderKeeperApp',
    bootstrapConfig: {
        strictDi: true
    },
    resolve: {
        APP_CONFIG: ['$http', function ($http) {
            return $http.get('/config/config.json');
        }]
    },
    onError: function (error) {
        alert('Could not bootstrap, error: ' + error);
    }
});