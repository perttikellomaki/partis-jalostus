angular.module('cachedResource', [])
    .provider('CachedResourceService', function () {
	function uri2key (uri) {
	    return uri.split("/")[2];
	}

	this.$get = ['$rootScope', '$resource', '$q', function ($rootScope, $resource, $q) {
	    return {
		make: function (resource_uri, params, localStorageService) {

		    var resource = $resource(resource_uri, params);

		    return {
			query: function(params) {

			    return resource.query(params);
			},
			get: function(params) {

			    var deferred = $q.defer();

			    var uri = params.uri;
			    params.key = uri2key(params.uri);

			    var cached_value = localStorageService.get(uri);

			    var threshold_minutes = 10;
			    var threshold = threshold_minutes * 60 * 1000;

			    if (cached_value
				&& (new Date()) - (new Date(cached_value.refresh_time_from_server)) < threshold) {

				// if value found in cache, create a new resource
				// and copy the cached properties into it
				var returned_instance = new resource;
				for (var p in cached_value) {
				    if (p[0] != '$') {
					returned_instance[p] = cached_value[p];
				    }
				}
				deferred.resolve(returned_instance);
			    } else {
				if (cached_value) {
				    console.log("cached value expired: " + JSON.stringify(cached_value))
				}
				console.log("fetch from server " + uri);
				delete params['uri'];
				var instance_from_server = resource.get(params);
				instance_from_server.$promise.then(function (response) {
				    var res = response;
				    res.refresh_time_from_server = new Date();
				    localStorageService.set(uri, JSON.stringify(res));
				    deferred.resolve(res);
				});
			    }
			    
			    return deferred.promise;
			},
			makeNew: function () {
			    if (arguments.length == 0) {
				return new resource();
			    } else if (arguments.length == 1) {
				return new resource(arguments[0]);
			    } else {
				console.log("make_new: cannot handle more than one argument");
			    }
			},
			save: function (instance, parameters, callback) {

			    var params = {}
			    if (arguments.length >= 2) {
				params = parameters;
			    }
			    if (instance.uri != undefined) {
				params.key = uri2key(instance.uri);
			    } else {
				params.key = '';
			    }
			    if (arguments.length == 3) {
				instance.$save(params, 
					       function (entity) {
						   entity.refresh_time_from_server = new Date();
						   localStorageService.set(entity.uri, JSON.stringify(entity));
						   callback(entity);
					       });
			    } else {
				instance.$save(params,
					       function (entity) {
						   entity.refresh_time_from_server = new Date();
						   localStorageService.set(entity.uri, JSON.stringify(entity));
					       });
			    }
			    
			},
			delete: function (instance, succ, err) {

			    if (arguments.length == 3) {
				instance.$delete({key: uri2key(instance.uri)}, succ, err);
			    } else if (arguments.length == 2) {
				instance.$delete({key: uri2key(instance.uri)}, succ);
			    } else {
				instance.$delete({key: uri2key(instance.uri)});
			    }
			}

		    }
		}
	    }
	}]
    })