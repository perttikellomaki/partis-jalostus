'use strict';


// Declare app level module which depends on filters, and services
angular.module('myApp', ['myApp.filters', 'myApp.services', 'myApp.directives', 'ngResource', 'ui.bootstrap', 'ui.date', 'ngGrid']).
  config(['$routeProvider', function($routeProvider) {
    $routeProvider.when('/etusivu', {templateUrl: 'etusivu/etusivu.html', controller: EtusivuCtrl});
    $routeProvider.when('/koirat', {templateUrl: 'partials/koirat.html', controller: KoiratCtrl});
    $routeProvider.when('/koira', {templateUrl: 'koira/uusi_koira.html', controller: UusiKoiraCtrl});
    $routeProvider.when('/koira/perustiedot/Koira/:key', {templateUrl: 'koira/koira.html', controller: KoiraPerustiedotCtrl});
    $routeProvider.when('/koira/sukupuu/Koira/:key', {templateUrl: 'koira/koira_sukupuu.html', controller: KoiraSukupuuCtrl});
    $routeProvider.when('/koira/paimennustaipumus/Koira/:key', {templateUrl: 'koira/koira_paimennustaipumus.html', controller: KoiraPaimennustaipumusCtrl});
    $routeProvider.when('/login', {templateUrl: 'partials/login.html', controller: LoginCtrl});
    $routeProvider.otherwise({redirectTo: '/etusivu'});
  }])
    .run(['$rootScope', '$http',
	  function ($rootScope, $http) {
	      $rootScope.typeaheadUros = function (name) {
		  return $http.get("/KoiraAutoComplete?sukupuoli=uros&prefix=" + encodeURIComponent(name))
		      .then(function (response) { return response.data });
	      }			
	      $rootScope.typeaheadNarttu = function (name) {
		  return $http.get("/KoiraAutoComplete?sukupuoli=narttu&prefix=" + encodeURIComponent(name))
		      .then(function (response) { return response.data });
	      }
	      $rootScope.dateToYYYYMMDD = function (date) {
		  // convert date to "yyyy-mm-dd"
		  var bds = date.getFullYear()
		      + "-"
		      + ("0" + (date.getMonth() + 1)).slice(-2)
		      + "-"
		      + ("0" + date.getDate()).slice(-2);
		  return bds;
	      }
	  }])
;
