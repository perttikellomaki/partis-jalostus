function KoiraSukupuuCtrl ($scope, $routeParams, $timeout, KoiraService, SidepanelService) {
    $scope.sidepanel = SidepanelService.get();
    $scope.sidepanel.selection = 'sukupuu';

    function updatePedigree (generations) {
	var dog_grid = []
	var arr = []
	for (var r=0; r < Math.pow(2,generations-1); r++) {
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
		dog_grid_row.push({});
	    }
	    arr.push(row);
	    dog_grid.push(dog_grid_row);
	}
	$scope.pedigree = arr;
	$scope.dog_grid = dog_grid;
    }

    $scope.generations_text = "3";
    updatePedigree(4);
    
    $scope.updateGenerations = function () {
	var gens = parseInt($scope.generations_text);
	if (gens != NaN && gens > 2) {
	    if (gens < 6) {
		updatePedigree(gens+1);
	    } else {
		$scope.status = "Muodostetaan...";
		$timeout(function () {
		    updatePedigree(gens+1);
		    $scope.status = "Muodostetaan... valmis";
		}, 500);
	    }
	}
    }

    $scope.koira
	= KoiraService.get({uri: '/Koira/' + $routeParams.key});

    $scope.editing = false;

    $scope.edit = function () {
	$scope.editing = true;
    }

    $scope.save = function () {
	$scope.$broadcast('PedigreeSave');
	$scope.editing = false;
    }
}
KoiraSukupuuCtrl.$inject = ['$scope', '$routeParams', '$timeout', 'KoiraService', 'SidepanelService'];

function PedigreeCellCtrl ($scope, $location, KoiraService) {
    $scope.this_cell_dog = {};
    $scope.name = '';
    
    var row = $scope.element.row;
    var col = $scope.element.col;
    var desc_row = $scope.element.descendant;
    var desc_col = $scope.element.col -1;
    $scope.desc_row = desc_row;
    $scope.desc_col = desc_col;

    if (col == 0) {
	$scope.koira.Then(function (response) {
	    var koira = response.resource;
	    $scope.this_cell_dog = koira;
	    $scope.name = koira.virallinen_nimi;
	    $scope.dog_grid[0][0] = koira;
	});
    } else {
	if ($scope.element.sex == 0) {
	    $scope.$watch(
		'dog_grid[desc_row][desc_col].isa',
		function (new_val) {
		    if (new_val != undefined) {
			KoiraService.get({uri: new_val})
			    .Then(function (response) {
				var dog = response.resource;
				$scope.this_cell_dog = dog;
				$scope.name = dog.virallinen_nimi;
				$scope.dog_grid[row][col]
				    = $scope.this_cell_dog;
			    });
		    }
		});
	} else {
	    $scope.$watch(
		'dog_grid[desc_row][desc_col].ema',
		function (new_val) {
		    if (new_val != undefined) {
			KoiraService.get({uri: new_val})
			    .Then(function (response) {
				var dog = response.resource;
				$scope.this_cell_dog = dog;
				$scope.name = dog.virallinen_nimi;
				$scope.dog_grid[row][col]
				    = $scope.this_cell_dog;
			    });
		    }
		});
	}
    }

    $scope.gotoDog = function () {
	$location.path('/koira/perustiedot' 
			+ $scope.this_cell_dog.uri);
    }

    function updateDogEntry () {
	var dog = KoiraService.query({virallinen_nimi: $scope.name});
	dog.thenServer(function (response) {
	    var dogs = response.resource;
	    if (dogs.length == 0) {
		if (confirm("Koiraa "
			    + $scope.name
			    + " ei löydy tietokannasta. Lisätäänkö?")) {
		    // FIXME: dry
		    $scope.this_cell_dog = KoiraService.makeNew();
		    $scope.dog_grid[row][col] = $scope.this_cell_dog;
		    KoiraService.save(
			$scope.this_cell_dog,
			{virallinen_nimi: $scope.name,
			 sukupuoli: $scope.element.sex == 0 ? 'uros' : 'narttu'},
			function (new_dog) {
			    var descendant = $scope.dog_grid[desc_row][desc_col];
			    if ($scope.element.sex == 0) {
				descendant.isa = new_dog.uri;
			    } else {
				descendant.ema = new_dog.uri;
			    }
			    KoiraService.save(descendant, {key: uri2key(descendant.uri)});
			});
		}
	    } else if (dogs.length == 1) {
		var original = $scope.name;
		if ($scope.name.split(' ').length == 1) {
		    $scope.name = prompt("Koiran '"
					 + original
					 + "' nimessä ei ole kenneliä, ja tietokannassa "
					 + "on saman niminen koira. Jos tarkoitat "
					 + "tietokannassa jo olevaa koiraa, jätä nimi ennalleen. "
					 + "Muussa tapauksessa lisää nimeen jotain, jolla sen "
					 + "erottaa eri koiraksi (vuosiluku, selite, tms.).",
					 original);
		}
		if ($scope.name == original) {
		    $scope.this_cell_dog = dogs[0];
		    $scope.dog_grid[row][col] = $scope.this_cell_dog;
		    var descendant = $scope.dog_grid[desc_row][desc_col];
		    if ($scope.element.sex == 0) {
			descendant.isa = $scope.this_cell_dog.uri;
		    } else {
			descendant.ema = $scope.this_cell_dog.uri;
		    }
		    KoiraService.save(descendant, {key: uri2key(descendant.uri)});
		} else {

		    // FIXME: dry
		    $scope.this_cell_dog = KoiraService.makeNew();
		    $scope.dog_grid[row][col] = $scope.this_cell_dog;
		    KoiraService.save(
			$scope.this_cell_dog,
			{virallinen_nimi: $scope.name,
			 sukupuoli: $scope.element.sex == 0 ? 'uros' : 'narttu'},
			function (new_dog) {
			    var descendant = $scope.dog_grid[desc_row][desc_col];
			    if ($scope.element.sex == 0) {
				descendant.isa = new_dog.uri;
			    } else {
				descendant.ema = new_dog.uri;
			    }
			    KoiraService.save(descendant, {key: uri2key(descendant.uri)});
			});
		}
	    }
	});
    }

    $scope.$on(
	'PedigreeSave',
	function () {
	    if ($scope.this_cell_dog.virallinen_nimi == undefined) {
		if ($scope.name.length == 0) {
		} else {
		    updateDogEntry();
		}
	    } else {
		if ($scope.this_cell_dog.virallinen_nimi == $scope.name) {
		} else {
		    updateDogEntry();
		}
	    }
	}); 
}
PedigreeCellCtrl.$inject = ['$scope', '$location', 'KoiraService'];
