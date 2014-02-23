function KennelAdminCtrl ($scope, $routeParams, KennelService, SidepanelService) {
    SidepanelService.get().selection = 'admin';
    KennelService.get({uri: '/Kennel/' + $routeParams.key})
	.Then(function (response) {
	    $scope.kennel = response.resource;
	});

    $scope.save = function () {
	KennelService.save($scope.kennel,
			   function () { alert("Talletettu"); });
    }
}
KennelAdminCtrl.$inject = ['$scope', '$routeParams', 'KennelService', 'SidepanelService'];
