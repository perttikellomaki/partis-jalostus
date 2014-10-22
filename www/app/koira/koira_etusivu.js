function KoiraEtusivuCtrl($scope) {
}
KoiraEtusivuCtrl.$inject = ['$scope'];

function SearchKoiraCtrl($scope, $http, $location, $modal, KoiraService, TypeaheadService) {

    $scope.koira = KoiraService.makeNew();
    $scope.typeahead = TypeaheadService.typeahead;
    $scope.typeaheadClear = TypeaheadService.clear;

    $scope.gotoDog = function(name) {
        var dogs = KoiraService.query({virallinen_nimi: name});
        dogs.thenServer(function(response) {
            var results = response.resource;
            if (results.length == 0) {
                open();
            } else if (results.length > 1) {
                alert("Samannimisiä koiria löytyi useita, ota yhteyttä tietokannan ylläpitäjään.");
            } else {
                $location.path("/koira/perustiedot" + results[0].uri);
            }
        });
    }
    $scope.items = ['item1', 'item2', 'item3'];

    function open(size) {

        var modalInstance = $modal.open({
            templateUrl: 'uusi_koira.html',
            controller: UusiKoiraCtrl,
            size: size,
            resolve: {
                koira: function() {
                    return $scope.koira
                }
            }
        });

        modalInstance.result.then(function(koira) {
            $location.path("/koira/perustiedot" + koira.uri);
        });
    }
    ;
}
SearchKoiraCtrl.$inject = ['$scope', '$http', '$location', '$modal', 'KoiraService', 'TypeaheadService'];


function UusiKoiraCtrl($scope, $location, $modalInstance, KoiraService, TypeaheadService, koira) {
    $scope.koira = koira;
    $scope.sexes = [{sex: 'uros'}, {sex: 'narttu'}];
    $scope.selected = $scope.sexes[0];


    $scope.ok = function() {
        KoiraService.save($scope.koira,
                {key: '', sukupuoli: $scope.selected.sex},
        function(koira) {
            $modalInstance.close($scope.koira);
        });
        TypeaheadService.clear();
    };

    $scope.cancel = function() {
        $modalInstance.dismiss('cancel');
    };
}
UusiKoiraCtrl.$inject = ['$scope', '$location', '$modalInstance', 'KoiraService', 'TypeaheadService', 'koira'];
