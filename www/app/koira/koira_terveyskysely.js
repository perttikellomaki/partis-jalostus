function KoiraTerveyskyselyCtrl ($scope, $routeParams, KoiraService, TerveyskyselyService, SidepanelService) {
    SidepanelService.get().selection = 'terveyskysely';
    $scope.koira = KoiraService.get({uri: "/Koira/" + $routeParams.key});
    $scope.kysely = TerveyskyselyService.makeNew();
    $scope.kyselyt = [];
    $scope.send = function () {
	$scope.kysely.timestamp = new Date();  // fixme: remove once saved on server
	$scope.create_new = false;
	$scope.kyselyt.push($scope.kysely);
	$scope.kysely = TerveyskyselyService.makeNew();
    }
}
KoiraTerveyskyselyCtrl.$inject = ['$scope', '$routeParams', 'KoiraService', 'TerveyskyselyService', 'SidepanelService'];

