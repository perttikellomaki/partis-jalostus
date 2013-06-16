'use strict';

/* Controllers */

function uri2key (uri) {
    return uri.split("/")[2];
}


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

    $scope.modtimes = KoiraService.query({key: '', modtime_only: true});

    $scope.myData = [];

    $scope.gridOptions = {data: 'myData',
			  displaySelectionCheckbox: false,
			  columnDefs: [{field: 'virallinen_nimi',
					displayName: 'Virallinen nimi',
					cellTemplate: '<div><a href="/#/koira{{row.entity.uri}}">{{row.entity[col.field]}}</a></div>'
				       }
				       ]
			 };
}
KoiratCtrl.$inject = ['$scope', 'KoiraService'];

function LoginStatusCtrl ($scope, $resource) {
    var resource = $resource("/LoginStatus");
    var status = resource.get();
    $scope.login_status = status;
    $scope.$on('LoginStatusChanged', function (event, path) {
	$scope.login_status = resource.get();
    })
}
LoginStatusCtrl.$inject = ['$scope', '$resource']

function LoginCtrl ($scope, $rootScope, $resource) {
    var federated_resource = $resource("/FederatedLogin")
    $scope.providers = federated_resource.query();

    var password_request_resource = $resource("/PasswordRequest",
					      {email: '@email',
					       nickname: '@nickname',
					       status_message: '@status_message',
					       secret: '@secret'})
    $scope.request = new password_request_resource();
    $scope.request.status_message = '';
    $scope.askPassword = function () {
	$scope.request.$save()
    }

    var local_login_resource = $resource("/LocalLogin",
					 {email: '@email',
					  password: '@password',
					  status_message : '@status_message'});
    $scope.local_login = new local_login_resource();
    $scope.login = function () {
	$scope.local_login.$save(function () {
	    $rootScope.$broadcast('LoginStatusChanged', '');
	});
    }
}
LoginCtrl.$inject = ['$scope', '$rootScope', '$resource']

function LeftcolCtrl ($scope, $location, SidepanelService) {
    $scope.sidepanel = SidepanelService.get();

    $scope.path_start = $location.path().split("/")[1];

    $scope.$on('$locationChangeSuccess',
	       function (event, new_path) {
		   $scope.path_start = $location.path().split("/")[1];
		  });

    $scope.setSelection = function (selection) {
	$scope.sidepanel.selection = selection;
    }
}
LeftcolCtrl.$inject = ['$scope', '$location', 'SidepanelService'];
