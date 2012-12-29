'use strict';

/* Controllers */


function KoiratCtrl($scope, KoiraService) {
    $scope.koirat = KoiraService.query({key: ''},
				       function (nodes) {
					   var tmp = [];
					   for (var n in nodes) {
					       var node = nodes[n];
					       tmp.push(node);
					   }
					   $scope.myData = tmp;
				       });

    $scope.myData = [];

    $scope.gridOptions = {data: 'myData',
			  displaySelectionCheckbox: false,
			  columnDefs: [{field: 'virallinen_nimi',
					displayName: 'Virallinen nimi',
					cellTemplate: '<div><a href="/#/koira{{row.entity.uri}}">{{row.entity[col.field]}}</a></div>'
				       }
				       ]
			 };
}
KoiratCtrl.$inject = ['$scope', 'KoiraService'];

function KoiraCtrl($scope, $resource, $routeParams, KoiraService) {
    if ($routeParams.key == undefined) {
	$scope.koira_history = []
	$scope.koira = KoiraService.makeNew();
	$scope.existing_koira = false;
    } else {
	var history_resource = $resource("/History/:key");
	$scope.koira_history = history_resource.query({key: $routeParams.key})
	$scope.koira = KoiraService.get({key: $routeParams.key});
	$scope.koira_show_history = false;
	$scope.existing_koira = true;
    }

    $scope.save = function () {
	if ($routeParams.key == undefined) {
	    $scope.koira.$save({key: ''});
	} else {
	    $scope.koira.$save({key: $routeParams.key});
	}
	$scope.editing = false;
    }

    $scope.editing = false;

    $scope.toggleEdit = function () {
	$scope.editing = !$scope.editing;
    }
}
KoiraCtrl.$inject = ['$scope', '$resource', '$routeParams', 'KoiraService'];

function PaimennusCtrl ($scope, $resource, $routeParams) {
    var paimennus_resource = $resource("/Paimennustaipumus",
				       {koira: '@koira',
					kiinnostus: '@kiinnostus',
					taipumus: '@taipumus',
					henkinen_kestavyys: '@henkinen_kestavyys',
					ohjattavuus: '@ohjattavuus',
					tuomari: '@tuomari',
					paikka: '@paikka',
					paiva: '@paiva'});
    $scope.tests = paimennus_resource.query({koira: $routeParams.key});
    $scope.new_test = false;
    $scope.newTest = function () {
	$scope.new_test = new paimennus_resource();
    }

    $scope.saveTest = function () {
	$scope.new_test.$save({koira: $routeParams.key});
    }
    $scope.expanded = false;
    $scope.toggleExpand = function () {
	$scope.expanded = !$scope.expanded;
    }
}
PaimennusCtrl.$inject = ['$scope', '$resource', '$routeParams'];
