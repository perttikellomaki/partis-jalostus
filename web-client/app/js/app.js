'use strict';


// Declare app level module which depends on filters, and services
angular.module('myApp', ['myApp.filters', 'myApp.services', 'myApp.directives', 'ngResource', 'ui', 'ngGrid']).
  config(['$routeProvider', function($routeProvider) {
    $routeProvider.when('/koirat', {templateUrl: 'partials/koirat.html', controller: KoiratCtrl});
    $routeProvider.when('/koira', {templateUrl: 'koira/uusi_koira.html', controller: UusiKoiraCtrl});
    $routeProvider.when('/koira/Koira/:key', {templateUrl: 'koira/koira.html', controller: KoiraCtrl});
    $routeProvider.when('/login', {templateUrl: 'partials/login.html', controller: LoginCtrl});
    $routeProvider.otherwise({redirectTo: '/koirat'});
  }]);
