function AdminSidepanelCtrl ($scope, $routeParams, $location, SidepanelService) {
    $scope.gotoSubview = function (subview) {
	$location.path('/admin/' + subview + '/Admin/' + $routeParams.key);
    }
}
AdminSidepanelCtrl.$inject = ['$scope', '$routeParams', '$location', 'SidepanelService'];

function AdminCtrl ($scope, SidepanelService, ProfileService, RoleService, DogOwnerRoleService) {
    $scope.profiles = ProfileService.query();

    $scope.role = RoleService.makeNew();

    $scope.newRole = function () {
	RoleService.save($scope.role, {},
			 function () {
			     $scope.profiles = ProfileService.query();
			 });
    }

    $scope.dog_owner_roles = DogOwnerRoleService.query({valid: false});
}
AdminCtrl.$inject = ['$scope', 'SidepanelService', 'ProfileService', 'RoleService', 'DogOwnerRoleService'];

function ProfileListRowCtrl ($scope, RoleService) {
    $scope.roles = RoleService.query({user_id: $scope.profile.user_id});
}
ProfileListRowCtrl.$inject = ['$scope', 'RoleService'];

function AdminUnconfirmedOwnerRowCtrl ($scope, KoiraService, RoleService) {
    $scope.dog = KoiraService.get({uri: $scope.role.dog});

    $scope.confirm = function () {
	$scope.role.valid = true;
	RoleService.save($scope.role)
    }
    $scope.unconfirm = function () {
	$scope.role.valid = false;
	RoleService.save($scope.role)
    }
}
AdminUnconfirmedOwnerRowCtrl.$inject = ['$scope', 'KoiraService', 'RoleService'];
