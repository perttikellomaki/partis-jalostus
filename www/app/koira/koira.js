function KoiraPerustiedotCtrl($scope, $resource, $routeParams, $location, $http, KoiraService, SidepanelService) {
    $scope.dateOptions = {
        changeYear: true,
        changeMonth: true,
        yearRange: '1900:-0'
    };

    $scope.sidepanel = SidepanelService.get();
    $scope.sidepanel.selection = '';

    $scope.sexes = [{sex: 'uros'}, {sex: 'narttu'}];
    $scope.birthday = {};
    var history_resource = $resource("/History/:key");
    $scope.koira_history = history_resource.query({key: $routeParams.key})
    $scope.koira = KoiraService.get({key: $routeParams.key});

    $scope.koira.$then(
	function (response) {
	    var koira = response.resource;
	    if (koira.syntymapaiva != undefined 
		&& koira.syntymapaiva.length > 0) {
		var date = new Date(koira.syntymapaiva);
		$scope.birthday.date = date;
		$scope.birthday.date_string = 
		    date.getDate()
		    + "." + (date.getMonth() + 1)
		    + "." + date.getFullYear();
	    }
	    $scope.timestamp = new Date(koira.timestamp);
	    if (koira.sukupuoli == 'uros') {
		$scope.selected_sex = $scope.sexes[0];
	    } else {
		$scope.selected_sex = $scope.sexes[1];
	    }
	});

    $scope.$watch(
	"selected_sex.sex",
	function (new_val, old_val) {
	    $scope.koira.sukupuoli = new_val;
	});		  

    $scope.$watch(
	"birthday.date",
	function (new_val, old_val) {
	    if (new_val != undefined) {
		$scope.koira.syntymapaiva =
		    new_val.getFullYear()
		    + "-" + (new_val.getMonth() + 1)
		    + "-" + new_val.getDate();
		console.log($scope.koira.syntymapaiva);
		$scope.birthday.date_string = 
		    new_val.getDate()
		    + "." + (new_val.getMonth() + 1)
		    + "." + new_val.getFullYear();
		$scope.koira.syntymavuosi = new_val.getFullYear();
	    }
	})

    $scope.$watch(
	"koira.isa",
	function (new_val, old_val) {
	    if (new_val != undefined 
		&& new_val.length > 0) {
		KoiraService.get({uri: new_val})
		    .$then(function (response) {
			var isa = response.resource;
			$scope.isa_nimi = isa.virallinen_nimi;
		    });
	    }
	});

    $scope.$watch(
	"koira.ema",
	function (new_val, old_val) {
	    if (new_val != undefined 
		&& new_val.length > 0) {
		KoiraService.get({uri: new_val})
		    .$then(function (response) {
			var ema = response.resource;
			$scope.ema_nimi = ema.virallinen_nimi;
		    });
	    }
	});

    $scope.$watch(
	"koira.ema",
	function (new_val, old_val) {
	    if (new_val != undefined 
		&& new_val.length > 0) {
		KoiraService.get({uri: new_val})
		    .$then(function (response) {
			var ema = response.resource;
			$scope.ema_nimi = ema.virallinen_nimi;
		    });
	    }
	});

    $scope.koira_show_history = false;
    $scope.editing = false;
    
    $scope.save = function () {

	function handleEma() {
	    if ($scope.ema_nimi != undefined && $scope.ema_nimi.length > 0) {
		var ema = KoiraService.query({virallinen_nimi: $scope.ema_nimi});
		ema.$then(function (response) {
		    var dogs = response.resource;
		    if (dogs.length == 0) {
			if (confirm("Emää ei löydy tietokannasta. Lisätäänkö?")) {
			    var inserted = KoiraService.makeNew();
			    inserted.$save(
				{virallinen_nimi: $scope.ema_nimi,
				 sukupuoli: 'narttu'},
				function (ema) {
				    $scope.koira.ema = ema.uri;
				    console.log($scope.koira);
				    $scope.koira.$save({key: $routeParams.key});
				});
			}
		    } else if (dogs.length == 1) {
			$scope.koira.ema = dogs[0].uri;
			console.log($scope.koira);
			$scope.koira.$save({key: $routeParams.key});
		    }
		})
	    } else {
		$scope.koira.$save({key: $routeParams.key});
	    }
	    $scope.koira_history = history_resource.query({key: $routeParams.key})
	}

	if ($scope.isa_nimi != undefined && $scope.isa_nimi.length > 0) {
	    var isa = KoiraService.query({virallinen_nimi: $scope.isa_nimi});
	    isa.$then(function (response) {
		var dogs = response.resource;
		if (dogs.length == 0) {
		    if (confirm("Isää ei löydy tietokannasta. Lisätäänkö?")) {
			var inserted = KoiraService.makeNew();
			inserted.$save(
			    {virallinen_nimi: $scope.isa_nimi,
			     sukupuoli: 'uros'},
			    function (isa) {
				$scope.koira.isa = isa.uri;
				console.log($scope.koira);
				handleEma();
			    });
		    }
		} else if (dogs.length == 1) {
		    $scope.koira.isa = dogs[0].uri;
		    console.log($scope.koira);
		    handleEma();
		}
	    })
	} else {
	    handleEma();
	}
	$scope.editing = false;
    }

    $scope.birthdayChange = function () {
	var bds = $scope.birthday.date.getFullYear()
	    + "-"
	    + ("0" + ($scope.birthday.date.getMonth() + 1)).slice(-2)
	    + "-"
	    + ("0" + $scope.birthday.date.getDate()).slice(-2);
	$scope.koira.syntymapaiva = bds;
    }

    $scope.toggleEdit = function () {
	$scope.editing = !$scope.editing;
    }
}
KoiraPerustiedotCtrl.$inject = ['$scope', '$resource', '$routeParams', '$location', '$http', 'KoiraService', 'SidepanelService'];

function KoiraHistoryCtrl ($scope, KoiraService) {
    if ($scope.h.isa != undefined && $scope.h.isa.length > 0) {
	$scope.h_isa = KoiraService.get({uri: $scope.h.isa});
    }
    if ($scope.h.ema != undefined && $scope.h.ema.length > 0) {
	$scope.h_ema = KoiraService.get({uri: $scope.h.ema});
    }
    $scope.h_timestamp = new Date($scope.h.timestamp);
}
KoiraHistoryCtrl.$inject = ['$scope', 'KoiraService'];

function YhdistysPaimennustaipumusCtrl ($scope, YhdistysPaimennustaipumusService) {
    $scope.tests = [];
    $scope.$watch('koira.uri',
		  function (new_val) {
		      if (new_val != undefined) {
			  $scope.tests = YhdistysPaimennustaipumusService.query(
			      {koira: new_val})
		      }
		  });
}
YhdistysPaimennustaipumusCtrl.$inject = ['$scope', 'YhdistysPaimennustaipumusService'];

function UusiKoiraCtrl ($scope, $location, KoiraService) {
    $scope.sexes = [{sex: 'uros'}, {sex: 'narttu'}];
    $scope.selected = $scope.sexes[0];
    $scope.koira = KoiraService.makeNew();
    $scope.save = function () { 
	$scope.koira.$save({key: '', sukupuoli: $scope.selected.sex},
			   function (koira) {
			       $location.path("/koira/perustiedot" + koira.uri);
			   });
    }
}
UusiKoiraCtrl.$inject = ['$scope', '$location', 'KoiraService'];

function TerveyskyselyCtrl ($scope, TerveyskyselyService) {
    $scope.kysely = TerveyskyselyService.makeNew();

    $scope.send = function () {
	$scope.kysely.virallinen_nimi = $scope.koira.virallinen_nimi;
	$scope.kysely.$save();
    }
}
TerveyskyselyCtrl.$inject = ['$scope', 'TerveyskyselyService'];

function AutoimmuuniCtrl ($scope) {
}
AutoimmuuniCtrl.$inject = ['$scope'];

function KoiraSidepanelCtrl ($scope, $routeParams, $location, SidepanelService) {
    $scope.gotoSubview = function (subview) {
	$location.path('/koira/' + subview + '/Koira/' + $routeParams.key);
    }
}
KoiraSidepanelCtrl.$inject = ['$scope', '$routeParams', '$location', 'SidepanelService'];
