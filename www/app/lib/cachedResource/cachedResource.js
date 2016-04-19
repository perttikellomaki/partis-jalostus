var resource_url_prefix = '';
var running_under_phonegap = false;

angular.module('cachedResource', ['LocalStorageModule'])
    .provider('CachedResourceService', function () {
	function uri2key (uri) {
	    if (uri != undefined) {
		return uri.split("/")[2];
	    } else {
		return '';
	    }
	}

	this.$get = [
	    '$rootScope', '$resource', '$http', '$q', '$routeParams', 'OAuth2TokenService',
	    function ($rootScope, $resource, $http, $q, $routeParams, OAuth2TokenService) {
		return {
		    make: function (resource_uri, params, localStorageService) {

			var resource = $resource(resource_url_prefix + resource_uri, params);

			return {
			    query: function(params) {
				if (params == undefined) {
				    params = {};
				}

				if ($routeParams.sharingkey != undefined) {
				    params.sharing = "/Sharing/" + $routeParams.sharingkey;
				}

				var cached_result = false;
				var cached_result_validated = false;

				var result = [];

				if (params.clear_cache) {
				    delete params.clear_cache;
				    localStorageService.remove(resource_uri + "?" + JSON.stringify(params));
				}

				if (params.modtime_holder != undefined) {
				    var cached = localStorageService.get(resource_uri + "?" + JSON.stringify(params));
				    if (cached) {
					cached_result = [];
					for (var i = 0; i < cached.length; i++) {
					    var res = new resource();
					    for (var p in cached[i]) {
						res[p] = cached[i][p];
					    }
					    cached_result.push(res);
					    result.push(res);
					}
				    }
				}

				var server_result = false;

				result.thenCache = function (f) {
				    if (cached_result) {
					f(cached_result);
				    }
				}

				var delayed_server_thens = [];

				// .thenServer() callbacks may need to be
				// queued in case they are registered
				// before the server resource result is
				// created
				result.thenServer = function (f) {
				    if (server_result) {
					server_result.$promise.then(
					    function (res) { f({resource: res}); });
				    } else {
					if (cached_result_validated) {
					    f({resource: cached_result,
					       cached_result_validated: true});
					} else {
					    delayed_server_thens.push(f);
					}
				    }
				}

				function performServerQuery () {
				    function doQuery (depmod) {
					server_result = resource.query(params);
					server_result.$promise.then(
					    function (results) {
						// update result list with items from server
						for (var r = 0; r < results.length; r++) {
						    if (result.length < r) {
							result.push(results[r]);
						    } else {
							result[r] = results[r];
						    }
						}
						// if there are fewer results from server, delete
						// the extraneous ones
						if (results.length < result.length) {
						    result.splice(result.length - 1, result.length - results.length);
						}

						for (var i in delayed_server_thens) {
						    delayed_server_thens[i]({resource: results,
									     cached_result_validated: false});
						}
						if (params.modtime_holder != undefined) {
						    localStorageService.set(resource_uri + "?" + JSON.stringify(params),
									    results);
						}
						if (depmod != false) {
							var cached = localStorageService.get(resource_uri + "?" + JSON.stringify(params));
							if (cached) {
							    localStorageService.set("/DepModTime" + resource_uri + "?" + JSON.stringify(params),
										    depmod.depmodtime);
							}
						}
					    },
					    function (response) {
						if ($rootScope.user_logged_in && response.status == 401) {
						    $rootScope.user_logged_in = false;
						    $rootScope.user_is_admin = false;
						    $rootScope.USER_PROFILE = {};
						    alert("You session has expired, please log in again.");
						}
					    }
					);
				    }

				    var depmod = false;
				    if (params.modtime_holder == undefined) {
					doQuery(false);
				    } else {
					var depmod = $resource(resource_url_prefix + "/DepModTime/:key").get({key: uri2key(params.modtime_holder)});
					var cached_depmod = localStorageService.get("/DepModTime" + resource_uri + "?" + JSON.stringify(params));
					depmod.$promise.then(function (depmod) {
					    if (!cached_depmod) {
						doQuery(depmod);
					    } else {
						if (depmod.depmodtime != cached_depmod) {
						    doQuery(depmod);
						} else {
						    cached_result_validated = true;
						    for (var i in delayed_server_thens) {
							delayed_server_thens[i]({resource: cached_result,
										 cached_result_validated: true});
						    }
						}
					    }
					});
				    }
				}
				
				OAuth2TokenService.withAuthorization(performServerQuery);
				
				return result;
			    },
			    get: function(params) {

				if ($routeParams.sharingkey != undefined) {
				    params.sharing = "/Sharing/" + $routeParams.sharingkey;
				}

				var uri = params.uri;
				params.key = uri2key(params.uri);

				if (params.uri == undefined) {
				    uri = "/FakePrefix/" + params.key;
				}

				if (params.clear_cache) {
				    localStorageService.remove(uri);
				}

				// We return a new instance of the
				// resource, and modify it once there is
				// data.
				var returned_instance = new resource({uri: uri});
				var cached_instance = localStorageService.get(uri);
				var cached_instance_validated = false;
				var instance_from_server = false;
				
				if (cached_instance) {
				    for (var p in cached_instance) {
					if (p[0] != '$') {
					    returned_instance[p] = cached_instance[p];
					}
				    }
				}

				// Callback registration. Function f
				// is called either with the server
				// response, or a fake response from
				// the cache.
				var delayed_Then_successes = [];
				var delayed_Then_errors = [];
				returned_instance.Then = function (f, err) {

				    if (cached_instance_validated) {

					// cached instance validated
					// before callback
					// registration
					f({resource: returned_instance,
					   is_first_notification: true,
					   is_update: false,
					   is_validated: true});
				    } else if (cached_instance) {

					// cached instance not yet
					// validated, call callback
					// now, and again once
					// validity established
					f({resource: returned_instance,
					   is_first_notification: true,
					   is_update: false,
					   is_validated: false});
					if (instance_from_server) {
					    instance_from_server.$promise.then(
						function (resource) {
						    // new value is
						    // only fetched if
						    // there are
						    // changes
						    f({resource: resource,
						       is_update: true,
						       is_first_notification: false,
						       is_validated: true})
						},
						function () {
						    if (err != undefined) {
							err.apply(this, arguments);
						    }
						});
					} else {
					    // cached instance
					    // validation still in
					    // progress
					    delayed_Then_successes.push(f);
					    if (err != undefined) {
						delayed_Then_errors.push(err);
					    }
					}
				    } else {
					// there was no cached
					// instance, so the instance
					// from server is not an
					// update
					instance_from_server.$promise.then(
					    function (resource) {
						f({resource: resource,
						   is_update: false,
						   is_first_notification: true,
						   is_validated: true});
					    },
					    function () {
						if (err != undefined) {
						    err.apply(this, arguments);
						}
					    });
				    }
				}

				function performServerGet (is_update) {
				    instance_from_server = resource.get(params);
				    instance_from_server.$promise.then(
					function (resource) {
					    localStorageService.set(uri, JSON.stringify(resource));

					    for (var p in resource) {
						if (p[0] != '$') {
						    returned_instance[p] = resource[p];
						}
					    }

					    // run any queued success callbacks
					    for (var i in delayed_Then_successes) {
						delayed_Then_successes[i]({
						    resource: resource,
						    is_update: is_update,
						    is_first_notification: false,
						    is_validated: true});
					    }
					},
					function (response) {
					    if ($rootScope.user_logged_in && response.status == 401) {
						$rootScope.user_logged_in = false;
						$rootScope.user_is_admin = false;
						$rootScope.USER_PROFILE = {};
						alert("You session has expired, please log in again.");
					    } else {
						// run any queued error callbacks
						for (var i in delayed_Then_errors) {
						    delayed_Then_errors[i](response);
						}
					    }
					});
				}

				if (params.modtime != undefined
				    && cached_instance
				    && params.modtime == cached_instance.modtime) {
				    cached_instance_validated = true;
				} else if (cached_instance && cached_instance.uri != undefined) {
				    OAuth2TokenService.withAuthorization(
					function () {
					    $resource(resource_url_prefix + "/ModTime/:key").get({key: uri2key(cached_instance.uri)})
						.$promise.then(
						    function (modtime) {
							if (modtime.modtime == cached_instance.modtime) {
							    cached_instance_validated = true;
							    for (var i in delayed_Then_successes) {
								delayed_Then_successes[i]({resource: returned_instance,
											   is_first_notification: false,
											   is_update: false,
											   is_validated: true});
							    }
							} else {
							    performServerGet(true);
							}
						    },
						    function () { 
							console.log("ERR " + JSON.stringify(arguments)); 
							performServerGet(true);  // argument does not really matter as we expect an error
						    }
						);
					});
				} else {
				    OAuth2TokenService.withAuthorization(
					function () { performServerGet(false); });
				}

				return returned_instance;
			    },
			    makeNew: function () {
				if (arguments.length == 0) {
				    return new resource();
				} else if (arguments.length == 1) {
				    return new resource(arguments[0]);
				} else {
				    console.log("makeNew: cannot handle more than one argument");
				}
			    },
			    save: function (instance, parameters, callback) {
				var save_arguments = arguments;
				var params = {}
				if (save_arguments.length >= 2) {
				    params = parameters;
				}
				var modified = params.force_write ? true : false;
				if (instance.uri == undefined) {
				    modified = true;
				} else {
				    var cached_instance = localStorageService.get(instance.uri);
				    if (cached_instance == null) {
					modified = true;
				    } else {
					for (var p in instance) {
					    if (p[0] != '$' 
						&& p != 'Then' 
						&& cached_instance[p] != instance[p]) {
						modified = true;
						break;
					    }
					}
				    }
				}
				if (instance.uri != undefined) {
				    params.key = uri2key(instance.uri);
				} else {
				    params.key = '';
				}
				if (modified) {
				    localStorageService.set(instance.uri, instance);
				    OAuth2TokenService.withAuthorization(
					function () {
					    function err (response) {
						alert("There was an error: " + JSON.stringify(response.data));
					    }
					    if (save_arguments.length == 3) {
						instance.$save(params, 
							       function (inst) {
								   localStorageService.set(inst.uri, inst);  // to set modtime in cache
								   callback(inst)
							       }, err);
					    } else {
						instance.$save(params,
							       function (inst) {
								   localStorageService.set(inst.uri, inst)  // to set modtime in cache
							       }, err);
					    }
					});
				} else {
				    if (save_arguments.length == 3) {
					// call the callback
					// immediately if there were
					// no changes to propagate to
					// server
					callback(instance);
				    }
				}
			    },
			    delete: function (instance, succ, err) {
				var delete_arguments = arguments;
				OAuth2TokenService.withAuthorization(
				    function () {

					if (delete_arguments.length == 3) {
					    instance.$delete({key: uri2key(instance.uri)}, succ, err);
					} else if (delete_arguments.length == 2) {
					    instance.$delete({key: uri2key(instance.uri)}, succ);
					} else {
					    instance.$delete({key: uri2key(instance.uri)});
					}
				    });
			    },
			    drop: function (uri) {
				localStorageService.remove(uri);
			    },
                            copy: function (original) {
                                var copy = new resource();
                                for (var p in original) {
                                    if (p[0] != "$" && p != "uri") {
                                        copy[p] = original[p];
                                    }
                                }
                                return copy;
                            }
			}
		    }
		}
	    }]
    })
    .factory('OAuth2TokenService',
	     ['$http', '$rootScope', '$resource', '$window', 'localStorageService', '$timeout', '$location', '$q',
	      function ($http, $rootScope, $resource, $window, localStorageService, $timeout, $location, $q) {
	          // See http://code.google.com/p/google-api-javascript-client/wiki/Authentication
		  var OAUTH2_SCOPE = 'https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/youtube.upload';
		  var OAUTH2_TOKEN_TYPE = 'Bearer';

		  var endpoint = "https://accounts.google.com/o/oauth2/auth";
		  var endtoken = "https://accounts.google.com/o/oauth2/token"; // token endpoint
		  var response_type = "code";

		  // ## Update this value: The client_id obtained during application registration ##
		  //var client_id = "115935478491-e89m7tj9bbhauf0avobm6m0eubvl1nn6.apps.googleusercontent.com";
		  var client_id = "554004680997.apps.googleusercontent.com";
		  
		  // ## Update this value: The client secret obtained during application registration ##
		  //var client_secret = "V2iTRzwuYa7XaU8K7I5G03D4"; 		
		  var client_secret = "4w1N0lvW-z3H3seXr9QfpxYJ"; 	
		  
		  // or urn:ietf:wg:oauth:2.0:oob
		  var redirect_uri = "http://localhost"; 				 

		  // The URI registered with the application
		  var redirect_url_token = ""; 						

		  var scope = OAUTH2_SCOPE;
		  
		  /* As defined in the OAuth 2.0 specification, this field must contain a value 
		   * of "authorization_code" or "refresh_token" */			
		  var grantTypes = { AUTHORIZE: "authorization_code", REFRESH: "refresh_token" }; 
		  
		  var access_type = "offline";
		  
		  // ## Not required to be updated: only used for echoing ##
		  var state = "lligtaskinit"

		  var authUri = endpoint + '?' 
		      + 'scope=' + encodeURIComponent(scope) 
		      + '&' + 'redirect_uri=' + encodeURIComponent(redirect_uri) 
		      + '&' + 'response_type=' + encodeURIComponent(response_type) 
		      + '&' + 'client_id=' + encodeURIComponent(client_id)
		      + '&' + 'state=' + encodeURIComponent(state)
		      + '&' + 'access_type=' + encodeURIComponent(access_type)
		      + '&' + 'approval_prompt=force'; // @TODO - check if we really need this param

		  function getRefreshToken (auth_code) {
		      var deferred = $q.defer();
		      try {
			  $.ajax({type: 'POST',
				  url: endtoken,
				  data: {
				      client_id: client_id,
				      client_secret: client_secret,
				      code: auth_code,
				      redirect_uri: redirect_uri,
				      grant_type: grantTypes.AUTHORIZE}
				 })
			      .done(function (data) {
				  localStorageService.set('oauth2_refresh_token', data.refresh_token);
				  localStorageService.set(
				      'oauth2_access_token_entry',
				      {value: data.access_token,
				       expires: new Date((new Date()).getTime() + 1000*parseInt(data.expires_in))});
				  $http.defaults.headers.common['Authorization'] = OAUTH2_TOKEN_TYPE + ' ' + data.access_token;
				  $rootScope.$apply(function () { deferred.resolve(data.refresh_token); });
			      })
			      .fail(function(xhr) {
				  $rootScope.$apply(function () { deferred.reject(xhr.responseText); });
			      });
		      } catch(err) {
			  $rootScope.$apply(function () { deferred.reject(err.message); });
		      }
		      return deferred.promise;
		  }

		  function getAccessToken () {

		      if (!running_under_phonegap) {
			  return;
		      }

		      var refresh_token = localStorageService.get('oauth2_refresh_token')
		      var deferred = $q.defer();
		      try {
			  $.ajax({type: 'POST',
				  url: endtoken,
				  data: {
				      client_id: client_id,
				      client_secret: client_secret,
				      refresh_token: refresh_token,
				      grant_type: grantTypes.REFRESH}
				 })
			      .done(function (data) {
				  var current_access_token = {
				      value: data.access_token,
				      expires: new Date((new Date()).getTime() + 1000*parseInt(data.expires_in))}
				  localStorageService.set('oauth2_access_token_entry', current_access_token);
				  $rootScope.$apply(function () {
				      deferred.resolve(current_access_token);
				  });
			      })
			      .fail(function(xhr) {

				  console.log("FAILURE GETTING NEW ACCESS TOKEN " + xhr.responseText);
				  $rootScope.$apply(function (){ 
				      deferred.reject(xhr.responseText);
				  });
			      });
		      } catch(err) {
			  console.log("GET_ACCESS_TOKEN ERROR " + err.message);
		      }
		      return deferred.promise;
		  }

		  function minutesUntilAccessTokenExpiration (token_entry) {
		      if (token_entry) {
			  var time_left_ms = new Date(token_entry.expires) - (new Date());
			  return time_left_ms*1000*60;
		      } else {
			  return 0;
		      }
		  }

		  var token_fetch_in_progress = false;
		  var pending_token = false;

		  function withAuthorization (f) {
		      if (!running_under_phonegap) {
			  f();
			  return;
		      } 

		      var expiration_threshold = 15;  // start worrying when this many minutes left
		      var validity_threshold = 5;     // consider token valid if at least this many minutes left
		      
		      var token_entry = localStorageService.get('oauth2_access_token_entry');
		      var timeleft = minutesUntilAccessTokenExpiration(token_entry);
		      if (timeleft > validity_threshold) {
			  $http.defaults.headers.common['Authorization'] = 'Bearer' + ' ' + token_entry.value;
			  f();

			  // expiration approaching, get a new token while the old one is still valid
			  if (timeleft < expiration_threshold && !token_fetch_in_progress) {
			      console.log("token expiration approaching, fetching a new one");
			      token_fetch_in_progress = true;
			      getAccessToken()
				  .then(function () {
				      token_fetch_in_progress = false;
				  });
			  }
		      } else {
			  // token expired
			  if (pending_token == false) {
			      pending_token = getAccessToken();
			  }
			  pending_token
			      .then(
				  function (token_entry) {
				      $http.defaults.headers.common['Authorization'] = 'Bearer' + ' ' + token_entry.value;
				      pending_token = false;
				      f();
				  },
				  function () { 
				      // show token alerts once a minute maximum
				      if (previous_token_failure == false 
					  || (new Date()) - previous_token_failure > 60*1000) {
					  alert("Authorization using Google's servers failed!"); 
					  previous_token_failure = new Date();
				      }
				      pending_token = false;
				  });
		      }
		  }
		  
		  return {
		      getRefreshToken: getRefreshToken,
		      getAccessToken: getAccessToken,
		      withAuthorization: withAuthorization,
		      authUri : function () { return authUri; }
		  }
	      }])
