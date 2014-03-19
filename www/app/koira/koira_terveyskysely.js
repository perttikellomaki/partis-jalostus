function KoiraTerveyskyselyCtrl ($scope, $routeParams, KoiraService, TerveyskyselyService, SidepanelService, LoginService) {
    SidepanelService.get().selection = 'terveyskysely';
    $scope.koira = KoiraService.get({uri: "/Koira/" + $routeParams.key});
    $scope.kysely = TerveyskyselyService.makeNew();
    $scope.kyselyt = [];
    $scope.createNew = function () {
	$scope.kysely.vastaaja = LoginService.nick();
	$scope.kysely.koira = $scope.koira.virallinen_nimi;
	$scope.create_new = true;
    }
    $scope.send = function () {
	$scope.kysely.timestamp = new Date();  // fixme: remove once saved on server
	$scope.create_new = false;
	$scope.kyselyt.push($scope.kysely);
	$scope.kysely = TerveyskyselyService.makeNew();
    }
}
KoiraTerveyskyselyCtrl.$inject = ['$scope', '$routeParams', 'KoiraService', 'TerveyskyselyService', 'SidepanelService', 'LoginService'];
