function TerveyskyselyKysymyksetCtrl($scope, SurveyService, SurveyQuestionService, TerveyskyselyService) {

    $scope.kyselyt = TerveyskyselyService.query();
    $scope.kyselyt.thenServer(function(response) {
        $scope.kysely = response.resource[0];
        $scope.surveys = SurveyService.query({working_copy_of: $scope.kysely.uri});
        $scope.surveys.thenServer(function(response) {
            var surveys = response.resource;
            if (surveys.length > 0) {
                $scope.working_copy = surveys[0];
                $scope.working_copy_exists = true;
                $scope.questions = SurveyQuestionService.query({survey: $scope.working_copy.uri});
                $scope.questions.thenServer(function(response) {
                    var questions = response.resource;
                    $scope.last_index = questions.length + 1;
                });
            } else {
                $scope.working_copy_exists = false;
            }
        })
    });

    $scope.createWorkingCopy = function() {
        $scope.working_copy =
                SurveyService.makeNew({working_copy_of: $scope.kysely.uri,
                    title: $scope.kysely.title + " (työkopio)"});
        SurveyService.save($scope.working_copy, {}, function() {
            $scope.working_copy_exists = true;
            var original_questions = SurveyQuestionService.query({survey: $scope.kysely.uri});
            original_questions.thenServer(function(response) {
                var original_questions = response.resource;
                $scope.questions = [];
                for (var i = 0; i < original_questions.length; i++) {
                    var original_question = original_questions[i];
                    var question = SurveyQuestionService.copy(original_question);
                    question.working_copy_of = original_question.uri;
                    question.survey = $scope.working_copy.uri;
                    $scope.questions.push(question)
                    SurveyQuestionService.save(question)
                }
                $scope.last_index = $scope.questions.length + 1;
            });
        });
    };

    $scope.deleteWorkingCopy = function() {
        var to_delete = $scope.questions.length;

        function maybeDeleteSurvey() {
            if (to_delete == 0 || to_delete == 1) {
                SurveyService.delete($scope.working_copy, function() {
                    $scope.working_copy_exists = false;
                });
                to_delete = -1;
            } else {
                to_delete--;
            }
        }

        for (var i = 0; i < $scope.questions.length; i++) {
            SurveyQuestionService.delete($scope.questions[i], maybeDeleteSurvey);
        }
        maybeDeleteSurvey();
    };

    $scope.publishWorkingCopy = function() {
        var to_save = $scope.questions.length;

        function maybeDeleteSurvey() {
            if (to_save == 0 || to_save == 1) {
                $scope.deleteWorkingCopy();
                to_save = -1;
            } else {
                to_save--;
            }
        }
        
        function publishQuestion(question, position) {
            question.position = position;
            if (question.working_copy_of != undefined) {
                // this is a working copy of an existing question
                var original = SurveyQuestionService.get({uri: question.working_copy_of});
                original.Then(function(response) {
                    if (response.is_validated) {
                        var resource = response.resource;
                        for (var p in question) {
                            if (p[0] != "$"
                                    && p != "uri"
                                    && p != "survey"
                                    && p != "working_copy_of") {
                                resource[p] = question[p];
                            }
                        }
                        SurveyQuestionService.save(resource, {}, function() {
                            maybeDeleteSurvey();
                        })
                    }
                });
            } else {
                // this is a new question, create a new question and save it
                // so that this one can be deleted
                var new_question = SurveyQuestionService.copy(question);
                new_question.survey = $scope.kysely.uri;
                console.log("save new question")
                console.log(new_question)
                SurveyQuestionService.save(new_question, {}, maybeDeleteSurvey);
            }
        }

        for (var i = 0; i < $scope.questions.length; i++) {
            publishQuestion($scope.questions[i], i)
        }
        
        // in case survey had no questions
        maybeDeleteSurvey();
    };

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
TerveyskyselyKysymyksetCtrl.$inject = ['$scope', 'SurveyService', 'SurveyQuestionService', 'TerveyskyselyService'];

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

function TerveyskyselyVastaaCtrl($scope, $location, SurveyQuestionService, TerveyskyselyService, TerveyskyselySubmissionService, LoginService, KoiraService) {
    console.log("terveyskyselyvastaactrl");
    $scope.questions_readonly = true;
    $scope.enableQuestions = function () {
        $scope.questions_readonly = false;
    };
    $scope.questionsDisabled = function() {
        if (LoginService.loggedIn()) {
            return $scope.koira === undefined;
        } else {
            return $scope.questions_readonly;
        }
    };
    $scope.logged_in = LoginService.loggedIn();
    $scope.kyselyt = TerveyskyselyService.query();
    $scope.kyselyt.thenServer(function(response) {
        $scope.kysely = response.resource[0];
        $scope.questions = SurveyQuestionService.query({survey: $scope.kysely.uri});
        $scope.submission = TerveyskyselySubmissionService.makeNew({survey: $scope.kysely.uri});
    });
    $scope.isCollapsed = true;
    $scope.showDogSearch = function() {
        $scope.isCollapsed = false;
    }
    $scope.sendAnswer = function() {
        var year = (new Date()).getFullYear();
	if ($scope.koira !== undefined) {
            $scope.submission.koira = $scope.koira.uri;
            $scope.submission.dog_name = $scope.koira.virallinen_nimi;
	} else if ($scope.dog_name !== undefined) {
            $scope.submission.dog_name = $scope.dog_name;
        }
        $scope.submission.year = year;
	$scope.submission.email = $scope.kysely.email;
        TerveyskyselySubmissionService.save($scope.submission, {},
                function(answer) {
		    var message = "Kiitos vastauksestasi! ";
                    $scope.$broadcast('saveAnswer', answer, year);
		    if (!LoginService.loggedIn()) {
			message += "\n\nSaat kohta sähköpostiisi linkin. "
			    + "Klikkaamalla sitä vahvistat täyttäneesi terveyskyselyn. "
			    + "Näin saamme karsittua pois spämmirobotit.";
		    } else if (!LoginService.hasRole("dog_owner", $scope.koira.uri)) {
			message += "\n\nSinua ei ole rekisteröity koiran omistajaksi, "
			    + "joten vastauksesi on talletettu mutta ylläpito varmistaa vielä "
			    + "että voit antaa koiran terveystietoja.";
		    }
		    alert(message);
		    $location.path("/terveyskysely/vastaukset");
                });
    }
    $scope.dogFound = function(dog) {
        $scope.koira = dog;
        $scope.isCollapsed = true;
    }
}
TerveyskyselyVastaaCtrl.$inject = ['$scope', '$location', 'SurveyQuestionService', 'TerveyskyselyService', 'TerveyskyselySubmissionService', 'LoginService', 'KoiraService'];

function TerveyskyselyQuestionAnswerCtrl($scope, SurveyAnswerService) {
    $scope.answer = SurveyAnswerService.makeNew(
            {survey_question: $scope.question.uri,
                position: $scope.question.position});
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
    $scope.$on('saveAnswer', function(event, survey_submission, year) {
        SurveyAnswerService.save($scope.answer,
                {survey_question: $scope.question.uri,
                    year: year,
                    survey_submission: survey_submission.uri});
    });
}
TerveyskyselyQuestionAnswerCtrl.$inject = ['$scope', 'SurveyAnswerService'];

function TerveyskyselyVastauksetCtrl($scope, TerveyskyselySubmissionService, TerveyskyselyService, SurveyQuestionService) {
    $scope.kyselyt = TerveyskyselyService.query();
    $scope.kyselyt.thenServer(function(response) {
        $scope.kysely = response.resource[0];
        $scope.questions = SurveyQuestionService.query({survey: $scope.kysely.uri});
    });
    $scope.submissions = TerveyskyselySubmissionService.query();
}
TerveyskyselyVastauksetCtrl.$inject = ['$scope', 'TerveyskyselySubmissionService', 'TerveyskyselyService', 'SurveyQuestionService'];

function TerveyskyselySubmissionHeadingReadonlyCtrl($scope, KoiraService, SurveyAnswerService) {
    if ($scope.submission.koira != undefined) {
        $scope.koira = KoiraService.get({uri: $scope.submission.koira});
    }
}
TerveyskyselySubmissionHeadingReadonlyCtrl.$inject = ['$scope', 'KoiraService', 'SurveyAnswerService']

function TerveyskyselySubmissionReadonlyCtrl($scope, KoiraService, SurveyAnswerService) {
    $scope.answers = SurveyAnswerService.query({survey_submission: $scope.submission.uri});
}
TerveyskyselySubmissionReadonlyCtrl.$inject = ['$scope', 'KoiraService', 'SurveyAnswerService']

function TerveyskyselyAnswerReadonlyCtrl($scope, SurveyQuestionService) {
    $scope.question = SurveyQuestionService.get({uri: $scope.answer.survey_question});
}
TerveyskyselyAnswerReadonlyCtrl.$inject = ['$scope', 'SurveyQuestionService'];

function TerveyskyselyQuestionSummaryCtrl($scope, SurveyAnswerSummaryService) {
    $scope.summaries = SurveyAnswerSummaryService.query({survey_question: $scope.question.uri});
}
TerveyskyselyQuestionSummaryCtrl.$inject = ['$scope', 'SurveyAnswerSummaryService'];

function TerveyskyselySidepanelCtrl($scope, $routeParams, $location, SidepanelService) {
    $scope.gotoSubview = function(subview) {
        $location.path('/terveyskysely/' + subview)
    }
}
TerveyskyselySidepanelCtrl.$inject = ['$scope', '$routeParams', '$location', 'SidepanelService'];

function TerveyskyselyKasiteltavatCtrl($scope, TerveyskyselySubmissionService) {
    $scope.confirm_dog_submissions = TerveyskyselySubmissionService.query({koira_defined: false, submitter_confirmed: true});
}
TerveyskyselyKasiteltavatCtrl.$inject = ['$scope', 'TerveyskyselySubmissionService'];

function canonicalName(name) {
    return name.toLowerCase().match(/\S+/g).join(' ');
}

function TerveyskyselyConfirmDogCtrl($scope, $modal, KoiraService, TerveyskyselySubmissionService) {
    var query = KoiraService.query({canonical_name: canonicalName($scope.submission.dog_name)});
    query.thenServer(function (result) {
        var dogs = result.resource;
        if (dogs.length == 1) {
            $scope.koira = dogs[0];
            $scope.originally_undefined = false;
        } else {
            $scope.originally_undefined = true;
        }
    });
    $scope.confirm = function () {
        $scope.submission.koira = $scope.koira.uri;
        TerveyskyselySubmissionService.save($scope.submission);
    };
        
    $scope.open = function(size) {

        var modalInstance = $modal.open({
            templateUrl: 'search_dog_modal.html',
            controller: TerveyskyselySelectDogCtrl,
            size: size,
            resolve: {
                candidate: function() {
                    return {virallinen_nimi: $scope.submission.dog_name};
                }
            }
        });

        modalInstance.result.then(function(koira) {
          $scope.koira = koira;
        });
    }
}
TerveyskyselyConfirmDogCtrl.$inject = ['$scope', '$modal', 'KoiraService', 'TerveyskyselySubmissionService'];

function TerveyskyselySelectDogCtrl($scope, $modalInstance, KoiraService, TypeaheadService, candidate) {
    $scope.candidate = candidate;
    
    $scope.ok = function() {
        var query = KoiraService.query({canonical_name: canonicalName(candidate.virallinen_nimi)});
        query.thenServer(function (result) {
                        var dogs = result.resource;
                        if (dogs.length === 1) {
                            TypeaheadService.clear();
                            $modalInstance.close(dogs[0]);
                        } else {
                            $modalInstance.dismiss('cancel');
                        }
        });
    };

    $scope.cancel = function() {
        $modalInstance.dismiss('cancel');
    };
}
TerveyskyselySelectDogCtrl.$inject = ['$scope', '$modalInstance', 'KoiraService', 'TypeaheadService', 'candidate'];