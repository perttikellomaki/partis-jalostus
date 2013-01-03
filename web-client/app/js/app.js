'use strict';


// Declare app level module which depends on filters, and services
angular.module('myApp', ['myApp.filters', 'myApp.services', 'myApp.directives', 'ngResource', 'ngGrid']).
  config(['$routeProvider', function($routeProvider) {
    $routeProvider.when('/koirat', {templateUrl: 'partials/koirat.html', controller: KoiratCtrl});
    $routeProvider.when('/koira', {templateUrl: 'partials/koira.html', controller: KoiraCtrl});
    $routeProvider.when('/koira/Koira/:key', {templateUrl: 'partials/koira.html', controller: KoiraCtrl});
    $routeProvider.when('/login', {templateUrl: 'partials/login.html', controller: LoginCtrl});
    $routeProvider.otherwise({redirectTo: '/koirat'});
  }]);
