'use strict';


// Declare app level module which depends on filters, and services
angular.module('myApp', ['ngRoute', 'myApp.filters', 'myApp.services', 'myApp.directives', 'ngResource', 'cachedResource', 'ui.bootstrap', 'ui.date', 'LocalStorageModule', 'ui.sortable']).
  config(['$routeProvider', function($routeProvider) {
    $routeProvider.when('/etusivu', {templateUrl: 'etusivu/etusivu.html', controller: EtusivuCtrl});
    $routeProvider.when('/koira_etusivu', {templateUrl: 'koira/koira_etusivu.html', controller: KoiraEtusivuCtrl});
    $routeProvider.when('/koira/perustiedot/Koira/:key', {templateUrl: 'koira/koira.html', controller: KoiraPerustiedotCtrl});
    $routeProvider.when('/koira/sukupuu/Koira/:key', {templateUrl: 'koira/koira_sukupuu.html', controller: KoiraSukupuuCtrl});
    $routeProvider.when('/koira/paimennustaipumus/Koira/:key', {templateUrl: 'koira/koira_paimennustaipumus.html', controller: KoiraPaimennustaipumusCtrl});
    $routeProvider.when('/koira/terveyskysely/Koira/:key', {templateUrl: 'koira/koira_terveyskysely.html', controller: KoiraTerveyskyselyCtrl});
    $routeProvider.when('/kennel_etusivu', {templateUrl: 'kennel/kennel_etusivu.html', controller: KennelEtusivuCtrl});
    $routeProvider.when('/kennel/koirat/Kennel/:key', {templateUrl: 'kennel/kennel_koirat.html', controller: KennelKoiratCtrl});
    $routeProvider.when('/kennel/muutokset/Kennel/:key', {templateUrl: 'kennel/kennel_muutokset.html', controller: KennelMuutoksetCtrl});
    $routeProvider.when('/kennel/admin/Kennel/:key', {templateUrl: 'kennel/kennel_admin.html', controller: KennelAdminCtrl});
    $routeProvider.when('/login', {templateUrl: 'partials/login.html', controller: LoginCtrl});
    $routeProvider.when('/terveyskysely/kysymykset', {templateUrl: '/terveyskysely/terveyskysely_kysymykset.html', controller: TerveyskyselyKysymyksetCtrl});
    $routeProvider.when('/terveyskysely/vastaa', {templateUrl: '/terveyskysely/terveyskysely_vastaa.html', controller: TerveyskyselyVastaaCtrl});
    $routeProvider.when('/terveyskysely/vastaukset', {templateUrl: '/terveyskysely/terveyskysely_vastaukset.html', controller: TerveyskyselyVastauksetCtrl});
    $routeProvider.when('/terveyskysely/vastaukset', {templateUrl: '/terveyskysely/terveyskysely_vastaukset.html', controller: TerveyskyselyVastauksetCtrl});
    $routeProvider.when('/terveyskysely/kasiteltavat', {templateUrl: '/terveyskysely/terveyskysely_kasiteltavat.html', controller: TerveyskyselyKasiteltavatCtrl});
    $routeProvider.when('/admin', {redirectTo: '/admin/admin'});
    $routeProvider.when('/admin/admin', {templateUrl: '/admin/admin.html', controller: AdminCtrl});

    $routeProvider.otherwise({redirectTo: '/etusivu'});
  }])
    .run(['$rootScope', '$http',
	  function ($rootScope, $http) {
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
