function KoiraEtusivuCtrl ($scope) {
}
KoiraEtusivuCtrl.$inject = ['$scope'];

function SearchKoiraCtrl ($scope, $http, $location, KoiraService, TypeaheadService) {

    $scope.typeahead = TypeaheadService.typeahead;

    $scope.gotoDog = function (name) {
	var dogs = KoiraService.query({virallinen_nimi: name});
	dogs.thenServer(function (response) {
	    var results = response.resource;
	    if (results.length == 0) {
		alert("Koiraa ei löydy.");
	    } else if (results.length > 1) {
		alert("Samannimisiä koiria löytyi useita, ota yhteyttä tietokannan ylläpitäjään.");
	    } else {
		$location.path("/koira/perustiedot" + results[0].uri);
	    }
	});
    }
}
SearchKoiraCtrl.$inject = ['$scope', '$http', '$location', 'KoiraService', 'TypeaheadService'];
