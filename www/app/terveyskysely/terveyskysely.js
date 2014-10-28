function TerveyskyselyKysymyksetCtrl($scope, SurveyQuestionService, TerveyskyselyService) {

    $scope.kyselyt = TerveyskyselyService.query();
    $scope.kyselyt.thenServer(function(response) {
        $scope.kysely = response.resource[0];
        $scope.questions = SurveyQuestionService.query({survey: $scope.kysely.uri});
        $scope.questions.thenServer(function(response) {
            var questions = response.resource;
            $scope.last_index = questions.length + 1;
        });
    })

    $scope.sortableOptions = {
        stop: function(e, ui) {
            var position = 1;
            for (var i = 0; i < $scope.questions.length; i++) {
                var question = $scope.questions[i];
                question.position = position++;
                SurveyQuestionService.save(question);
            }
        }
    }

    // new question
    $scope.question = SurveyQuestionService.makeNew();

    $scope.question_kinds = [{name: "Vapaa teksti", question_kind: "free_text"},
        {name: "Kyllä/ei", question_kind: "boolean"}];

    $scope.question_kind = {chosen: $scope.question_kinds[0]};

    $scope.newQuestion = function() {
        var question = $scope.question;
        question.position = $scope.last_index;
        question.survey = $scope.kysely.uri;
        question.question_kind = $scope.question_kind.chosen.question_kind;
        $scope.last_index = $scope.last_index + 1;
        $scope.question = SurveyQuestionService.makeNew();
        SurveyQuestionService.save(question,
                {},
                function(question) {
                    $scope.questions.push(question);
                });
    }
}
;
TerveyskyselyKysymyksetCtrl.$inject = ['$scope', 'SurveyQuestionService', 'TerveyskyselyService'];

function TerveyskyselyQuestionCtrl($scope, SurveyQuestionService) {
    $scope.editing = false;
    $scope.edit = function() {
        for (i in $scope.question_kinds) {
            if ($scope.question.question_kind == $scope.question_kinds[i].question_kind) {
                $scope.question_kind.chosen = $scope.question_kinds[i];
            }
        }
        $scope.editing = true;
    }
    $scope.save = function() {
        var question = $scope.question;
        console.log("question")
        console.log(question)
        $scope.question.question_kind = $scope.question_kind.chosen.question_kind;
        SurveyQuestionService.save($scope.question);
        $scope.editing = false;
    }
}
TerveyskyselyQuestionCtrl.$inject = ['$scope', 'SurveyQuestionService'];

function TerveyskyselyVastaaCtrl($scope, SurveyQuestionService, TerveyskyselyService, TerveyskyselyAnswerService) {
    $scope.kyselyt = TerveyskyselyService.query();
    $scope.kyselyt.thenServer(function(response) {
        $scope.kysely = response.resource[0];
        $scope.questions = SurveyQuestionService.query({survey: $scope.kysely.uri});
    });
    $scope.isCollapsed = true;
    $scope.showDogSearch = function () {
        $scope.isCollapsed = false;
    }
    $scope.sendAnswer = function() {
        var survey_answer = TerveyskyselyAnswerService.makeNew({survey: $scope.kysely.uri});
        survey_answer.dog = $scope.koira.uri;
        TerveyskyselyAnswerService.save(survey_answer, {},
                function(answer) {
                    $scope.$broadcast('saveAnswer', answer);
                });
    }
    $scope.dogFound = function (dog) {
        $scope.koira = dog;
        $scope.isCollapsed = true;
    }
}
TerveyskyselyVastaaCtrl.$inject = ['$scope', 'SurveyQuestionService', 'TerveyskyselyService', 'TerveyskyselyAnswerService'];

function TerveyskyselyQuestionAnswerCtrl($scope, SurveyQuestionAnswerService) {
    $scope.answer = SurveyQuestionAnswerService.makeNew({survey_question: $scope.question.uri});
    $scope.yesno = {}
    $scope.changeYesno = function(choice) {
        if (choice == 'yes') {
            $scope.yesno.yes = true;
            $scope.yesno.no = false;
            $scope.answer.yesno_answer = true;
        } else {
            $scope.yesno.yes = false;
            $scope.yesno.no = true;
            $scope.answer.yesno_answer = false;
        }
    };
    $scope.$on('saveAnswer', function(event, survey_answer) {
        SurveyQuestionAnswerService.save($scope.answer,
                {survey_question: $scope.question.uri,
                    survey_answer: survey_answer.uri})
    });
}
TerveyskyselyQuestionAnswerCtrl.$inject = ['$scope', 'SurveyQuestionAnswerService']

function TerveyskyselyVastauksetCtrl ($scope) {
}
TerveyskyselyVastauksetCtrl.$inject = ['$scope'];

function TerveyskyselySidepanelCtrl($scope, $routeParams, $location, SidepanelService) {
    $scope.gotoSubview = function(subview) {
        $location.path('/terveyskysely/' + subview)
    }
}
TerveyskyselySidepanelCtrl.$inject = ['$scope', '$routeParams', '$location', 'SidepanelService'];