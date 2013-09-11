'use strict';

/* Services */

function makeCachedResource (resource) {
    function uri2key (uri) {
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
	makeNew: function () {
	    return new resource();
	}
    }
};

angular.module('myApp.services', [])
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
				var instance_from_server = resource.get(params);
				instance_from_server.$then(function (response) {
				    var res = response.resource;
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
    .factory('KoiraService',
	     ['$resource', 'CachedResourceService', 'localStorageService',
	      function ($resource, CachedResourceService, localStorageService) {
		  return CachedResourceService.make(
		      '/Koira/:key',
		      {virallinen_nimi: '@virallinen_nimi',
		       kutsumanimi: '@kutsumanimi',				
		       kennel: '@kennel',
		       sukupuoli: '@sukupuoli',
		       syntymapaiva: '@syntymapaiva',
		       syntymavuosi: '@syntymavuosi',
		       isa: '@isa',
		       ema: '@ema'},
		      localStorageService);
	      }])
    .factory('YhdistysPaimennustaipumusService', 
	     function ($resource) {
		 return makeCachedResource(
		     $resource("/YhdistysPaimennustaipumus/:key",
			       {koira: '@koira',
				kiinnostus: '@kiinnostus',
				taipumus: '@taipumus',
				henkinen_kestavyys: '@henkinen_kestavyys',
				ohjattavuus: '@ohjattavuus',
				tuomari: '@tuomari',
				paikka: '@paikka',
				paiva: '@paiva',
				kommentit: '@kommentit'}));
	     })
    .factory('TerveyskyselyService',
	     function ($resource) {
		 return makeCachedResource(
		     $resource("/Terveyskysely/:key",
			       {koira: '@koira',
				virallinen_nimi: '@virallinen_nimi',
				autoimmuunisairaus: '@autoimmuunisairaus',
				slo: '@slo',
				imha: '@imha'}))
	     })
    .factory('SidepanelService',
	     function () {
		 var state = {};
		 return {
		     get: function () { return state; },
		 };
	     })
;
