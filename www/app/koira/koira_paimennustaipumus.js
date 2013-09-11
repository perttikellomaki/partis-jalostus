function KoiraPaimennustaipumusCtrl ($scope, $routeParams, KoiraService, SidepanelService, YhdistysPaimennustaipumusService) {
    $scope.sidepanel = SidepanelService.get();
    $scope.sidepanel.selection = 'paimennustaipumus';

    var koira_uri = '/Koira/' + $routeParams.key;

    $scope.koira
	= KoiraService.get({uri: koira_uri});

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
}
YhdistysPaimennustaipumusCtrl.$inject = ['$scope', 'YhdistysPaimennustaipumusService'];
