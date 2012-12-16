'use strict';

/* Controllers */


function KoiratCtrl($scope, KoiraService) {
    $scope.koirat = KoiraService.query({key: ''},
				       function (nodes) {
					   var tmp = [];
					   for (var n in nodes) {
					       var node = nodes[n];
					       tmp.push(node);
					   }
					   $scope.myData = tmp;
				       });

    $scope.myData = [];

    $scope.gridOptions = {data: 'myData',
			  displaySelectionCheckbox: false,
			  columnDefs: [{field: 'virallinen_nimi',
					displayName: 'Virallinen nimi',
					cellTemplate: '<div><a href="/#/koira{{row.entity.uri}}">{{row.entity[col.field]}}</a></div>'
				       },
				       {field: 'kutsumanimi',
					displayName: 'Kutsumanimi'}
				       ]
			 };
}
KoiratCtrl.$inject = ['$scope', 'KoiraService'];

function KoiraCtrl($scope, $resource, $routeParams, KoiraService) {
    if ($routeParams.key == undefined) {
	$scope.koira = KoiraService.makeNew();
    } else {
	$scope.koira = KoiraService.get({key: $routeParams.key});
    }
    $scope.save = function () {
	$scope.koira.$save({key: ''});
    }
}
KoiraCtrl.$inject = ['$scope', '$resource', '$routeParams', 'KoiraService'];
