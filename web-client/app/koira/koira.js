function KoiraCtrl($scope, $resource, $routeParams, $location, $http, KoiraService, SidepanelService) {
    $scope.sidepanel = SidepanelService.get();
    $scope.sidepanel.selection = '';

    $scope.birthday = {};
    var history_resource = $resource("/History/:key");
    $scope.koira_history = history_resource.query({key: $routeParams.key})
    $scope.koira = KoiraService.get(
	{key: $routeParams.key},
	function (koira) {
	    if (koira.syntymapaiva != undefined 
		&& koira.syntymapaiva.length > 0) {
		$scope.birthday.date = new Date(koira.syntymapaiva);
	    }
	    $scope.timestamp = new Date(koira.timestamp);
	});

    $scope.koira_show_history = false;
    $scope.editing = false;
    
    $scope.save = function () {
	$scope.koira.$save({key: $routeParams.key});
	$scope.koira_history = history_resource.query({key: $routeParams.key})
	$scope.editing = false;
    }

    $scope.birthdayChange = function () {
	var bds = $scope.birthday.date.getFullYear()
	    + "-"
	    + ("0" + ($scope.birthday.date.getMonth() + 1)).slice(-2)
	    + "-"
	    + ("0" + $scope.birthday.date.getDate()).slice(-2);
	$scope.koira.syntymapaiva = bds;
    }

    $scope.toggleEdit = function () {
	$scope.editing = !$scope.editing;
    }

    $scope.urokset = KoiraService.query({sukupuoli: "uros"});

    $scope.nartut = KoiraService.query({sukupuoli: "narttu"});

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

    $scope.typeahead = function (name) {
	return $http.get("/KoiraAutoComplete?prefix=" + encodeURIComponent(name))
	    .then(function (response) { return response.data });
    }			
}
KoiraCtrl.$inject = ['$scope', '$resource', '$routeParams', '$location', '$http', 'KoiraService', 'SidepanelService'];

function KoiraHistoryCtrl ($scope, KoiraService) {
    if ($scope.h.isa != undefined && $scope.h.isa.length > 0) {
	$scope.h_isa = KoiraService.get({uri: $scope.h.isa});
    }
    if ($scope.h.ema != undefined && $scope.h.ema.length > 0) {
	$scope.h_ema = KoiraService.get({uri: $scope.h.ema});
    }
    $scope.h_timestamp = new Date($scope.h.timestamp);
}
KoiraHistoryCtrl.$inject = ['$scope', 'KoiraService'];

function YhdistysPaimennustaipumusCtrl ($scope, YhdistysPaimennustaipumusService) {
    $scope.tests = [];
    $scope.$watch('koira.uri',
		  function (new_val) {
		      if (new_val != undefined) {
			  $scope.tests = YhdistysPaimennustaipumusService.query(
			      {koira: new_val})
		      }
		  });
}
YhdistysPaimennustaipumusCtrl.$inject = ['$scope', 'YhdistysPaimennustaipumusService'];

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
