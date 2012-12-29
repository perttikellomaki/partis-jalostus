'use strict';

/* Controllers */

function uri2key (uri) {
    return uri.split("/")[2];
}


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
    $scope.category_name = "paimennus";
    var paimennus_resource = $resource("/Paimennustaipumus/:key",
				       {koira: '@koira',
					kiinnostus: '@kiinnostus',
					taipumus: '@taipumus',
					henkinen_kestavyys: '@henkinen_kestavyys',
					ohjattavuus: '@ohjattavuus',
					tuomari: '@tuomari',
					paikka: '@paikka',
					paiva: '@paiva'});
    $scope.summary = "Ei testattu.";
    $scope.summarise = function () {
	var result = [];
	for (var e in $scope.entries) {
	    var res = $scope.entries[e].resource;
	    result.push(res.paiva
			+ " "
			+ res.kiinnostus + "/"
			+ res.taipumus + "/"
			+ res.henkinen_kestavyys + "/"
			+ res.ohjattavuus);
	}
	if (result.length > 0) {
	    $scope.summary = result.join(", ");
	}
    }
    $scope.entries = [];
    $scope.resources 
	= paimennus_resource.query(
	    {koira: $routeParams.key},
	    function () {
		for (var r in $scope.resources) {
		    $scope.entries.push({editing: false,
					 resource: $scope.resources[r]});
		    $scope.summarise();
		}
	    }
	);
    $scope.entry = false;
    $scope.newTest = function () {
	$scope.entry.resource = new paimennus_resource();
	$scope.entry.resource.koira = $routeParams.key;
    }

    $scope.save = function (entry) {
	entry.resource.$save({key: uri2key(entry.resource.uri)});
	entry.editing = false;
    }
    $scope.expanded = false;
    $scope.toggleExpand = function () {
	$scope.expanded = !$scope.expanded;
    }
    $scope.toggleEdit = function (entry) {
	entry.editing = !entry.editing;
    }
}
PaimennusCtrl.$inject = ['$scope', '$resource', '$routeParams'];
