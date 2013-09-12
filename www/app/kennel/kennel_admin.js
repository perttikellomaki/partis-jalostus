function KennelAdminCtrl ($scope, $routeParams, KennelService, SidepanelService) {
    SidepanelService.get().selection = 'admin';
    KennelService.get({uri: '/Kennel/' + $routeParams.key})
	.then(function (kennel) {
	    $scope.kennel = kennel;
	});

    $scope.save = function () {
	KennelService.save($scope.kennel,
			   function () { alert("Talletettu"); });
    }
}
KennelAdminCtrl.$inject = ['$scope', '$routeParams', 'KennelService', 'SidepanelService'];
