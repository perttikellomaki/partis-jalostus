'use strict';


// Declare app level module which depends on filters, and services
angular.module('myApp', ['myApp.filters', 'myApp.services', 'myApp.directives', 'ngResource', 'ui.bootstrap', 'ui.date', 'ngGrid']).
  config(['$routeProvider', function($routeProvider) {
    $routeProvider.when('/etusivu', {templateUrl: 'etusivu/etusivu.html', controller: EtusivuCtrl});
    $routeProvider.when('/koirat', {templateUrl: 'partials/koirat.html', controller: KoiratCtrl});
    $routeProvider.when('/koira', {templateUrl: 'koira/uusi_koira.html', controller: UusiKoiraCtrl});
    $routeProvider.when('/koira/perustiedot/Koira/:key', {templateUrl: 'koira/koira.html', controller: KoiraPerustiedotCtrl});
    $routeProvider.when('/koira/sukupuu/Koira/:key', {templateUrl: 'koira/koira_sukupuu.html', controller: KoiraSukupuuCtrl});
    $routeProvider.when('/login', {templateUrl: 'partials/login.html', controller: LoginCtrl});
    $routeProvider.otherwise({redirectTo: '/etusivu'});
  }]);
