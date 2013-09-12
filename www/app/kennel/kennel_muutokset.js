function KennelMuutoksetCtrl ($scope, $resource, $routeParams, KennelService, SidepanelService) {
    SidepanelService.get().selection = 'muutokset';

    var change_resource = $resource('/ChangeNotification');
    $scope.kennel = KennelService.get({uri: '/Kennel/' + $routeParams.key});
    $scope.kennel.then(function (kennel) {
	$scope.changes = change_resource.query({kennel: kennel.nimi});
    });
}
KennelMuutoksetCtrl.$inject = ['$scope', '$resource', '$routeParams', 'KennelService', 'SidepanelService'];

function KennelChangeCtrl ($scope, KoiraService) {
    $scope.koira = KoiraService.get({uri: $scope.change.koira});
    $scope.changed_entity_kind = $scope.change.changed_entity.split('/')[1];
}
KennelChangeCtrl.$inject = ['$scope', 'KoiraService'];
