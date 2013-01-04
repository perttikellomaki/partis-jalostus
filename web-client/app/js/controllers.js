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

function KoiraCtrl($scope, $resource, $routeParams, $location, KoiraService) {
    if ($routeParams.key == undefined) {
	$scope.koira_history = []
	$scope.koira = KoiraService.makeNew();
	$scope.existing_koira = false;
	$scope.editing = true;
    } else {
	var history_resource = $resource("/History/:key");
	$scope.koira_history = history_resource.query({key: $routeParams.key})
	$scope.koira = KoiraService.get({key: $routeParams.key});
	$scope.koira_show_history = false;
	$scope.existing_koira = true;
	$scope.editing = false;
    }

    $scope.save = function () {
	if ($routeParams.key == undefined) {
	    $scope.koira.$save({key: ''},
			       function (data) {
				   $location.path("/koira" + data.uri);
			       });
	} else {
	    $scope.koira.$save({key: $routeParams.key});
	    $scope.koira_history = history_resource.query({key: $routeParams.key})
	}
	$scope.editing = false;
    }

    $scope.toggleEdit = function () {
	$scope.editing = !$scope.editing;
    }
    $scope.items = KoiraService.query({key: ''});
    $scope.isa = {};
    $scope.$watch('koira.isa', 
		  function (new_val, old_val) {
		      if (new_val != undefined && new_val != "") {
			  $scope.isa = KoiraService.get({uri: new_val});
		      }
		  })
    $scope.ema = {};
    $scope.$watch('koira.ema', 
		  function (new_val, old_val) {
		      if (new_val != undefined && new_val != "") {
			  $scope.ema = KoiraService.get({uri: new_val});
		      }
		  })
}
KoiraCtrl.$inject = ['$scope', '$resource', '$routeParams', '$location', 'KoiraService'];

function setupScope($scope, $routeParams, $resource, resource) {
    $scope.category_name = "paimennus";
    $scope.entries = [];
    $scope.resources 
	= resource.query(
	    {koira: $routeParams.key},
	    function () {
		var history = $resource("/History/:key");
		for (var r in $scope.resources) {
		    var entry = {editing: false,
				 show_history: false,
				 resource: $scope.resources[r]};
		    entry.history =
			history.query({key: uri2key(entry.resource.uri)});
		    $scope.entries.push(entry);
		    $scope.summarise();
		}
	    }
	);
    $scope.entry = false;
    $scope.newEntry = function () {
	$scope.entry = {resource: new resource(),
			editing: true,
			show_history: false};
	$scope.entry.resource.koira = $routeParams.key;
    }
    $scope.save = function (entry) {
	if (entry.resource.uri == undefined) {
	    entry.resource.$save({key: ''});
	} else {
	    entry.resource.$save({key: uri2key(entry.resource.uri)});
	}
	entry.editing = false;
	$scope.entries.push(entry);
	$scope.entry = false;
    }
    $scope.expanded = false;
    $scope.toggleExpand = function () {
	$scope.expanded = !$scope.expanded;
    }
    $scope.toggleEdit = function (entry) {
	entry.editing = !entry.editing;
    }
}

function PaimennusCtrl ($scope, $resource, $routeParams) {
    setupScope($scope, $routeParams, $resource,
	       $resource("/Paimennustaipumus/:key",
			 {koira: '@koira',
			  kiinnostus: '@kiinnostus',
			  taipumus: '@taipumus',
			  henkinen_kestavyys: '@henkinen_kestavyys',
			  ohjattavuus: '@ohjattavuus',
			  tuomari: '@tuomari',
			  paikka: '@paikka',
			  paiva: '@paiva'}));
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
}
PaimennusCtrl.$inject = ['$scope', '$resource', '$routeParams'];

function LoginStatusCtrl ($scope, $resource) {
    var resource = $resource("/LoginStatus");
    var status = resource.get();
    $scope.login_status = status;
    $scope.$on('LoginStatusChanged', function (event, path) {
	$scope.login_status = resource.get();
    })
}
LoginStatusCtrl.$inject = ['$scope', '$resource']

function LoginCtrl ($scope, $rootScope, $resource) {
    var federated_resource = $resource("/FederatedLogin")
    $scope.providers = federated_resource.query();

    var password_request_resource = $resource("/PasswordRequest",
					      {email: '@email',
					       nickname: '@nickname',
					       status_message: '@status_message',
					       secret: '@secret'})
    $scope.request = new password_request_resource();
    $scope.request.status_message = '';
    $scope.askPassword = function () {
	$scope.request.$save()
    }

    var local_login_resource = $resource("/LocalLogin",
					 {email: '@email',
					  password: '@password',
					  status_message : '@status_message'});
    $scope.local_login = new local_login_resource();
    $scope.login = function () {
	$scope.local_login.$save(function () {
	    $rootScope.$broadcast('LoginStatusChanged', '');
	});
    }
}
LoginCtrl.$inject = ['$scope', '$rootScope', '$resource']
