'use strict';

/* Controllers */


function KoiratCtrl($scope, KoiraService) {
    $scope.koirat = KoiraService.query({key: ''});
}
KoiratCtrl.$inject = ['$scope', 'KoiraService'];

function KoiraCtrl($scope, $resource, $routeParams, KoiraService) {
    if ($routeParams.key == undefined) {
	$scope.koira = KoiraService.makeNew();
    }
    $scope.save = function () {
	$scope.koira.$save({key: ''});
    }
}
KoiraCtrl.$inject = ['$scope', '$resource', '$routeParams', 'KoiraService'];
