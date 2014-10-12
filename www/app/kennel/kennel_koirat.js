function KennelKoiratCtrl ($scope, $routeParams, KoiraService, KennelService, SidepanelService) {
    SidepanelService.get().selection = 'koirat';

    $scope.kennel = KennelService.get({uri: "/Kennel/" + $routeParams.key});
    $scope.kennel.Then(function (response) {
	if (response.is_first_notification) {
	    $scope.koirat = KoiraService.query({kennel: $scope.kennel.nimi});
	}
    });
}
KennelKoiratCtrl.$inject = ['$scope', '$routeParams', 'KoiraService', 'KennelService', 'SidepanelService'];
