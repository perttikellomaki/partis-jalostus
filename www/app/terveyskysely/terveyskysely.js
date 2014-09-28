function TerveyskyselyCtrl($scope, SurveyQuestionService) {
    $scope.questions = SurveyQuestionService.query();
    $scope.questions.thenServer(function (response) {
	var questions = response.resource;
	$scope.last_index = questions.length;
    });

    $scope.new_question = SurveyQuestionService.makeNew();

    $scope.kinds = [{name: "Vapaa teksti", kind: "free_text"},
		    {name: "Kyllä/ei", kind: "boolean"}];

    $scope.new_question_kind = $scope.kinds[0];

    $scope.newQuestion = function () {
	var new_question = $scope.new_question;
	new_question.position = $scope.last_index;
	$scope.last_index = $scope.last_index + 1;
	var kind = $scope.new_question_kind.kind;
	$scope.new_question = SurveyQuestionService.makeNew();
	SurveyQuestionService.save(
	    new_question, 
	    {kind: kind},
	    function (question) {
		$scope.questions.push(new_question);
	    });
    }
};
TerveyskyselyCtrl.$inject = ['$scope', 'SurveyQuestionService'];
