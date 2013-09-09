function KoiraSukupuuCtrl ($scope, $routeParams, KoiraService, SidepanelService) {
    $scope.sidepanel = SidepanelService.get();
    $scope.sidepanel.selection = 'sukupuu';

    var generations = 3;
    var dog_grid = []
    var arr = []
    for (var r=0; r < Math.pow(2,generations); r++) {
	var row = [];
	var dog_grid_row = [];
	for (var c=0; c < generations; c++) {
	    var rowspan = Math.pow(2, generations-c-1);
	    entry = {rowspan: rowspan,
		     sex: Math.floor(r / rowspan) % 2,
		     descendant:
		     Math.floor(r/(2*rowspan))*2*rowspan,
		     row: r,
		     col: c}
	    if ((r % Math.pow(2, generations-c-1))==0) {
		row.push(entry);
	    }
	    dog_grid_row.push(entry);
	}
	arr.push(row);
	dog_grid.push(dog_grid_row);
    }
    $scope.pedigree = arr;
    $scope.dog_grid = dog_grid;
    
    $scope.koira = KoiraService.get({uri: '/Koira/' + $routeParams.key});

    $scope.editing = false;

    $scope.edit = function () {
	$scope.editing = true;
    }

    $scope.save = function () {
	$scope.$broadcast('PedigreeSave');
	$scope.editing = false;
    }
}
KoiraSukupuuCtrl.$inject = ['$scope', '$routeParams', 'KoiraService', 'SidepanelService'];

function PedigreeCellCtrl ($scope, $location, KoiraService) {
    $scope.this_cell_dog = {};
    $scope.name = '';
    
    var row = $scope.element.row;
    var col = $scope.element.col;

    if (col == 0) {
	if ($scope.element.sex == 0) {
	    $scope.$watch(
		'koira.isa',
		function (new_val) {
		    if (new_val != undefined) {
			$scope.this_cell_dog = KoiraService.get({uri: new_val});
			$scope.this_cell_dog.$then(function (response) {
			    var dog = response.resource;
			    $scope.name = dog.virallinen_nimi;
			});
			$scope.dog_grid[row][col]
			    = $scope.this_cell_dog;
		    }
		});
	} else {
	    $scope.$watch(
		'koira.ema',
		function (new_val) {
		    if (new_val != undefined) {
			$scope.this_cell_dog = KoiraService.get({uri: new_val});
			$scope.this_cell_dog.$then(function (response) {
			    var dog = response.resource;
			    $scope.name = dog.virallinen_nimi;
			});
			$scope.dog_grid[row][col]
			    = $scope.this_cell_dog;
		    }
		});
	}
    } else {
	if ($scope.element.sex == 0) {
	    $scope.$watch(
		'dog_grid[element.descendant][element.col-1].isa',
		function (new_val) {
		    if (new_val != undefined) {
			$scope.this_cell_dog = KoiraService.get({uri: new_val});
			$scope.this_cell_dog.$then(function (response) {
			    var dog = response.resource;
			    $scope.name = dog.virallinen_nimi;
			});
			$scope.dog_grid[row][col]
			    = $scope.this_cell_dog;
		    }
		});
	} else {
	    $scope.$watch(
		'dog_grid[element.descendant][element.col-1].ema',
		function (new_val) {
		    if (new_val != undefined) {
			$scope.this_cell_dog = KoiraService.get({uri: new_val});
			$scope.this_cell_dog.$then(function (response) {
			    var dog = response.resource;
			    $scope.name = dog.virallinen_nimi;
			});
			$scope.dog_grid[row][col]
			    = $scope.this_cell_dog;
		    }
		});
	}
    }

    $scope.gotoDog = function () {
	$location.path('/koira/perustiedot' 
			+ $scope.this_cell_dog.uri);
    }

    $scope.$on(
	'PedigreeSave',
	function () {
	    if ($scope.this_cell_dog.virallinen_nimi == undefined) {
		if ($scope.name.length == 0) {
		    console.log("no change for empty entry");
		} else {
		    console.log("new dog " + $scope.name);
		}
	    } else {
		if ($scope.this_cell_dog.virallinen_nimi == $scope.name) {
		    console.log("no change for " + $scope.name);
		} else {
		    console.log("change " 
				+ $scope.this_cell_dog.virallinen_nimi 
				+ " to " + $scope.name);
		}
	    }
	});	       
}
PedigreeCellCtrl.$inject = ['$scope', '$location', 'KoiraService'];
