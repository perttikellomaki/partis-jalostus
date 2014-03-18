'use strict';

/* Controllers */

function uri2key (uri) {
    if (uri == undefined) {
	return undefined;
    } else {
	return uri.split("/")[2];
    }
}

function NavListController($scope, $location) {
    $scope.navClass = function (page) {
        var currentRoute = $location.path().split('/')[1];
	var result = page === currentRoute ? 'active' : '';
        return result;
    }
    $scope.gotoView = function (path) {
	$location.path(path);
    }
}
NavListController.$inject = ['$scope', '$location'];

function LoginStatusCtrl ($scope, $rootScope, $resource, LoginService) {
    var resource = $resource("/LoginStatus");
    var status = resource.get();
    status.$promise.then(function (response) {
	$rootScope.IS_ADMIN = response.is_admin;
	$rootScope.KENNEL = response.kennel;
	if (response.logged_in) {
	    LoginService.set(response.nick, response.kennel);
	}
    });
    $scope.login_status = status;
    $scope.$on('LoginStatusChanged', function (event, path) {
	$scope.login_status = resource.get();
    });
}
LoginStatusCtrl.$inject = ['$scope', '$rootScope', '$resource', 'LoginService']

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

    $scope.navClass = function (selection) {
	return selection === $scope.sidepanel.selection ? 'active' : '';
    }

}
LeftcolCtrl.$inject = ['$scope', '$location', 'SidepanelService'];

function HistoryCtrl ($scope, $resource) {
    var HistoryService = $resource('/History/:key');
    $scope.history = HistoryService.query({key: uri2key($scope.history_target)});
}
HistoryCtrl.$inject = ['$scope', '$resource'];

function HistoryItemCtrl ($scope, KoiraService) {
    var ignore_keys = ['author_nick', 'author', 'author_email', 'timestamp', 'uri'];
    $scope.entries = [];
    for (var p in $scope.h) {
	if (p[0] != '$' && ignore_keys.indexOf(p) == -1) {
	    (function () {
		var entry = {key: p, value: $scope.h[p]};
		if (entry.key == 'isa' || entry.key == 'ema' || entry.key == 'koira') {
		    var uri = entry.value;
		    entry.value = '';
		    KoiraService.get({uri: uri})
			.Then(function (response) {
			    var dog = response.resource;
			    entry.value = dog.virallinen_nimi;
			    console.log(entry);
			})
		}
		$scope.entries.push(entry);
	    })();
	}
    }
}
HistoryItemCtrl.$inject = ['$scope', 'KoiraService'];
