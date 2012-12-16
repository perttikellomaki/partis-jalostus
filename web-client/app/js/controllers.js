'use strict';

/* Controllers */


function KoiratCtrl($scope, KoiraService) {
    $scope.koirat = KoiraService.query({key: ''},
				       function (nodes) {
					   var tmp = [];
					   for (var n in nodes) {
					       var node = nodes[n];
					       console.log("NODE");
					       console.log(node);
					       tmp.push({virallinen_nimi: node.virallinen_nimi, 
							 kutsumanimi: node.kutsumanimi});
					   }
					   $scope.myData = tmp;
					   console.log($scope.myData);
				       });

    $scope.myData = [];

    $scope.gridOptions = {data: 'myData'};
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
