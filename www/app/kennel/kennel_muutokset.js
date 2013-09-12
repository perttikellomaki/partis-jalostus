function KennelMuutoksetCtrl ($scope, $routeParams, KennelService) {
    $scope.kennel = KennelService.get({uri: '/Kennel/' + $routeParams.key});
}
KennelMuutoksetCtrl.$inject = ['$scope', '$routeParams', 'KennelService'];
