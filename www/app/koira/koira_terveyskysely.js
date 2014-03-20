function KoiraTerveyskyselyCtrl ($scope, $routeParams, KoiraService, TerveyskyselyService, SidepanelService, LoginService) {
    SidepanelService.get().selection = 'terveyskysely';
    $scope.logged_in = LoginService.loggedIn();
    $scope.koira = KoiraService.get({uri: "/Koira/" + $routeParams.key});
    $scope.kysely = TerveyskyselyService.makeNew();
    $scope.kyselyt = TerveyskyselyService.query({koira: "/Koira/" + $routeParams.key,
						 modtime_holder: "/Koira/" + $routeParams.key});
    $scope.createNew = function () {
	$scope.kysely.vastaaja = LoginService.nick();
	$scope.kysely.koira = $scope.koira.uri;
	$scope.kysely.koira_virallinen_nimi = $scope.koira.virallinen_nimi;
	$scope.create_new = true;
    }
    $scope.send = function () {
	TerveyskyselyService.save(
	    $scope.kysely,
	    {},
	    function () { alert("Kiitos vastauksestasi!"); });
	$scope.create_new = false;
	$scope.kyselyt.push($scope.kysely);
	$scope.kysely = TerveyskyselyService.makeNew();
    }
}
KoiraTerveyskyselyCtrl.$inject = ['$scope', '$routeParams', 'KoiraService', 'TerveyskyselyService', 'SidepanelService', 'LoginService'];

