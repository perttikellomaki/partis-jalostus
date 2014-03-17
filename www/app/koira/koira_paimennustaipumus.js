function KoiraPaimennustaipumusCtrl ($scope, $routeParams, KoiraService, SidepanelService, YhdistysPaimennustaipumusService) {
    $scope.sidepanel = SidepanelService.get();
    $scope.sidepanel.selection = 'paimennustaipumus';

    var koira_uri = '/Koira/' + $routeParams.key;

    KoiraService.get({uri: koira_uri})
	.Then(function (response) {
	    $scope.koira = response.resource;
	});

    $scope.tests = YhdistysPaimennustaipumusService.query(
	{koira: koira_uri});

    $scope.newTest = function () {
	var test = YhdistysPaimennustaipumusService.makeNew();
	test.koira = koira_uri;
	$scope.tests.splice(0, 0, test);
    }
}
KoiraPaimennustaipumusCtrl.$inject = ['$scope', '$routeParams', 'KoiraService', 'SidepanelService', 'YhdistysPaimennustaipumusService'];

function YhdistysPaimennustaipumusCtrl ($scope, YhdistysPaimennustaipumusService) {
    $scope.history_target = $scope.test.uri;

    $scope.editing = ($scope.test.uri == undefined);

    $scope.edit = function () {
	$scope.editing = true;
    }

    $scope.save = function () {
	$scope.test.$save({key: uri2key($scope.test.uri)});
	$scope.editing = false;
    }

    $scope.verify = function () {
	$scope.test.verified = true;
	$scope.test.$save({key: uri2key($scope.test.uri)});
    }

    $scope.open = function($event) {
	console.log("open")
	$event.preventDefault();
	$event.stopPropagation();
	
	$scope.opened = true;
    };

    if ($scope.test.hyvaksytty) {
	$scope.test_hyvaksytty = {val: "true"};
    } else {
	$scope.test_hyvaksytty = {val: "false"};
    }	

    $scope.$watch('test_hyvaksytty.val', function (new_value) {
	if (new_value == 'true') {
	    $scope.test.hyvaksytty = true;
	} else if (new_value == 'false') {
	    $scope.test.hyvaksytty = false;
	}
    });
}
YhdistysPaimennustaipumusCtrl.$inject = ['$scope', 'YhdistysPaimennustaipumusService'];
