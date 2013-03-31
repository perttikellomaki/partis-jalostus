function KoiraCtrl($scope, $resource, $routeParams, $location, KoiraService) {
    var history_resource = $resource("/History/:key");
    $scope.koira_history = history_resource.query({key: $routeParams.key})
    $scope.koira = KoiraService.get({key: $routeParams.key});
    $scope.koira_show_history = false;
    $scope.editing = false;
    
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

function KoiraHistoryCtrl ($scope, KoiraService) {
    $scope.isa = '';
    $scope.ema = '';
    $scope.$watch('h',
		  function (new_val, old_val) {
		      if (new_val != undefined) {
			  if (new_val.isa != undefined 
			      && new_val.isa != '') {
			      $scope.isa = KoiraService.get({uri: new_val.isa});
			  }
			  if (new_val.ema != undefined 
			      && new_val.ema != '') {
			      $scope.ema = KoiraService.get({uri: new_val.ema});
			  }
		      }
		  });
}
KoiraHistoryCtrl.$inject = ['$scope', 'KoiraService'];

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

function UusiKoiraCtrl ($scope, $location, KoiraService) {
    $scope.koira = KoiraService.makeNew();
    $scope.save = function () { 
	$scope.koira.$save({key: ''},
			   function (koira) {
			       $location.path("/koira" + koira.uri);
			   });
    }
}
UusiKoiraCtrl.$inject = ['$scope', '$location', 'KoiraService'];
