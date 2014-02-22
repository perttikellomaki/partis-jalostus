function KoiraEtusivuCtrl ($scope) {
}
KoiraEtusivuCtrl.$inject = ['$scope'];

function SearchKoiraCtrl ($scope, $http, $location, KoiraService) {
    $scope.typeahead = function (name) {
	return $http.get("/KoiraAutoComplete?&prefix=" + encodeURIComponent(name))
	    .then(function (response) { return response.data });
    }

    $scope.gotoDog = function (name) {
	var dogs = KoiraService.query({virallinen_nimi: name});
	dogs.$promise.then(function (response) {
	    var results = response;
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
SearchKoiraCtrl.$inject = ['$scope', '$http', '$location', 'KoiraService'];
