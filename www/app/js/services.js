'use strict';

/* Services */

function makeCachedResource(resource) {
    function uri2key(uri) {
        return uri.split("/")[2];
    }
    return {
        query: function() {
            return resource.query.apply(this, arguments);
        },
        get: function() {
            // If the resource is addressed with an uri, replace the
            // uri with a corresponding key. This assumes that the
            // path given to $resource is of the form '/ResourceName/:key'
            if (arguments.length > 0 && typeof arguments[0] == "object") {
                var params = arguments[0];
                if (typeof params.uri != "undefined") {
                    params.key = uri2key(params.uri);
                    delete params.uri;
                }
            }
            return resource.get.apply(this, arguments);
        },
        makeNew: function() {
            return new resource();
        }
    }
}
;

angular.module('myApp.services', [])
        .factory('LoginService',
                ['RoleService', function(RoleService) {
                    var nick_;
                    var kennel_;
		    var roles_ = [];
                    var logged_in_ = false;
                    return {
                        set: function(nick, kennel) {
                            console.log("login service " + nick + " " + kennel)
                            nick_ = nick;
                            kennel_ = kennel;
                            if (nick != undefined) {
                                logged_in_ = true;
				roles_ = RoleService.query();
                            }
                        },
                        nick: function() {
                            console.log("nick " + nick_);
                            return nick_;
                        },
                        kennel: function() {
                            return kennel_;
                        },
                        loggedIn: function() {
                            return logged_in_;
                        },
			roles: function () {
			    return roles_;
			},
			hasRole: function (role, target) {
			    for (var i = 0; i < roles_.length; i++) {
				if (roles_[i].valid && roles_[i].role == role) {
				    if (role == "dog_owner") {
					return roles_[i].dog == target;
				    } else {
					return true;
				    }
				}
			    }
			    return false;
			}
                    };
                }])
        .factory('KoiraService',
                ['$resource', 'CachedResourceService', 'localStorageService',
                    function($resource, CachedResourceService, localStorageService) {
                        return CachedResourceService.make(
                                '/Koira/:key',
                                {virallinen_nimi: '@virallinen_nimi',
                                    kutsumanimi: '@kutsumanimi',
                                    kennel: '@kennel',
                                    sukupuoli: '@sukupuoli',
                                    syntymapaiva: '@syntymapaiva',
                                    syntymavuosi: '@syntymavuosi',
                                    isa: '@isa',
                                    ema: '@ema',
                                    verified: '@verified'},
                        localStorageService);
                    }])
        .factory('KennelService',
                ['CachedResourceService', 'localStorageService',
                    function(CachedResourceService, localStorageService) {
                        return CachedResourceService.make(
                                '/Kennel/:key',
                                {nimi: '@nimi',
                                    kasvattaja_email: '@kasvattaja_email'},
                        localStorageService);
                    }])
        .factory('YhdistysPaimennustaipumusService',
                function($resource) {
                    return makeCachedResource(
                            $resource("/YhdistysPaimennustaipumus/:key",
                                    {koira: '@koira',
                                        hyvaksytty: '@hyvaksytty',
                                        kiinnostus: '@kiinnostus',
                                        taipumus: '@taipumus',
                                        henkinen_kestavyys: '@henkinen_kestavyys',
                                        ohjattavuus: '@ohjattavuus',
                                        tuomari: '@tuomari',
                                        paikka: '@paikka',
                                        paiva: '@paiva',
                                        kommentit: '@kommentit',
                                        verified: '@verified'}));
                })
        .factory('SurveyService',
                ['CachedResourceService', 'localStorageService',
                    function(CachedResourceService, localStorageService) {
                        return CachedResourceService.make(
                                "/Survey/:key", {}, localStorageService)
                    }])
        .factory('SurveyQuestionService',
                ['CachedResourceService', 'localStorageService',
                    function(CachedResourceService, localStorageService) {
                        return CachedResourceService.make(
                                "/SurveyQuestion/:key", {}, localStorageService)
                    }])
        .factory('SurveySubmissionService',
                ['CachedResourceService', 'localStorageService',
                    function(CachedResourceService, localStorageService) {
                        return CachedResourceService.make(
                                "/SurveySubmission/:key", {}, localStorageService)
                    }])
        .factory('SurveyAnswerService',
                ['CachedResourceService', 'localStorageService',
                    function(CachedResourceService, localStorageService) {
                        return CachedResourceService.make(
                                "/SurveyAnswer/:key", {}, localStorageService)
                    }])
        .factory('SurveyAnswerSummaryService',
                ['CachedResourceService', 'localStorageService',
                    function(CachedResourceService, localStorageService) {
                        return CachedResourceService.make(
                                "/SurveyAnswerSummary/:key", {}, localStorageService)
                    }])
        .factory('RoleService',
                ['CachedResourceService', 'localStorageService',
                    function(CachedResourceService, localStorageService) {
                        return CachedResourceService.make(
                                "/Role/:key", {}, localStorageService)
                    }])
        .factory('DogOwnerRoleService',
                ['CachedResourceService', 'localStorageService',
                    function(CachedResourceService, localStorageService) {
                        return CachedResourceService.make(
                                "/DogOwnerRole/:key", {}, localStorageService)
                    }])
        .factory('ProfileService',
                ['CachedResourceService', 'localStorageService',
                    function(CachedResourceService, localStorageService) {
                        return CachedResourceService.make(
                                "/Profile/:key", {}, localStorageService)
                    }])
        .factory('TerveyskyselyService',
                ['CachedResourceService', 'localStorageService',
                    function(CachedResourceService, localStorageService) {
                        return CachedResourceService.make(
                                "/Terveyskysely/:key", {}, localStorageService)
                    }])
        .factory('TerveyskyselySubmissionService',
                ['CachedResourceService', 'localStorageService',
                    function(CachedResourceService, localStorageService) {
                        return CachedResourceService.make(
                                "/TerveyskyselySubmission/:key", {}, localStorageService)
                    }])
        .factory('SidepanelService',
                function() {
                    var state = {};
                    return {
                        get: function() {
                            return state;
                        },
                    };
                })
        .factory('TypeaheadService',
                ['$http', '$q', 'localStorageService',
                    function($http, $q, localStorageService) {
                        function makeTypeahead(prefix) {
                            function typeahead(name) {
                                var cached = localStorageService.get(prefix + encodeURIComponent(name));
                                if (cached) {
                                    var deferred = $q.defer();
                                    deferred.resolve(cached);
                                    return deferred.promise;
                                } else {
                                    return $http.get(prefix + encodeURIComponent(name))
                                            .then(function(response) {
                                                localStorageService.set(prefix + encodeURIComponent(name),
                                                        response.data);
                                                return response.data
                                            });
                                }
                            }
                            return typeahead;
                        }
                        function clear() {
                            var keys = localStorageService.keys();
                            for (var k in keys) {
                                // Only drop entries that are addressed with an uri.
                                // This keeps refresh tokens and the like in local storage.
                                var re = new RegExp("/KoiraAutoComplete");
                                if (keys[k].match(re)) {
                                    localStorageService.remove(keys[k]);
                                }
                            }
                        }
                        return {
                            typeahead: makeTypeahead("/KoiraAutoComplete?&prefix="),
                            typeaheadUros: makeTypeahead("/KoiraAutoComplete?sukupuoli=uros&prefix="),
                            typeaheadNarttu: makeTypeahead("/KoiraAutoComplete?sukupuoli=narttu&prefix="),
                            clear: clear
                        }
                    }])
        ;
