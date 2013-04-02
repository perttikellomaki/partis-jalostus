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
    .factory('KoiraService', 
	     function ($resource) {
		 return makeCachedResource(
		     $resource('/Koira/:key',
			       {virallinen_nimi: '@virallinen_nimi',
				kutsumanimi: '@kutsumanimi',				
				kennel: '@kennel',
				sukupuoli: '@sukupuoli',
				syntymapaiva: '@syntymapaiva',
				syntymavuosi: '@syntymavuosi',
				isa: '@isa',
				ema: '@ema'}))
	     })
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
				paiva: '@paiva'}));
	     })
    .factory('SidepanelService',
	     function () {
		 var state = {};
		 return {
		     get: function () { return state; },
		 };
	     })
;
