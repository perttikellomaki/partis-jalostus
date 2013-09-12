function KennelEtusivuCtrl ($scope, KennelService) {
    $scope.kennels = KennelService.query();
    $scope.new_kennel = KennelService.makeNew();
    $scope.create = function () {
	$scope.new_kennel.$save(
	    {key: ''},
	    function (kennel) {
		$scope.kennels.splice(0, 0, kennel);
		$scope.new_kennel = KennelService.makeNew();
	    });
    }
}
KennelEtusivuCtrl.$inject = ['$scope', 'KennelService'];
