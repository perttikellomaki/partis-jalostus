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
    .factory('LoginService',
	     function () {
		 var nick_;
		 var kennel_;
		 var logged_in_ = false;
		 return {
		     set: function (nick, kennel) {
			 console.log("login service " + nick + " " + kennel)
			 nick_ = nick;
			 kennel_ = kennel;
			 if (nick != undefined) {
			     logged_in_ = true;
			 }
		     },
		     nick: function () { console.log("nick " + nick_) ; return nick_; },
		     kennel: function () { return kennel_; },
		     loggedIn: function () { return logged_in_; }
		 };
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
		       ema: '@ema',
		       verified: '@verified'},
		      localStorageService);
	      }])
    .factory('KennelService',
	     ['CachedResourceService', 'localStorageService',
	      function (CachedResourceService, localStorageService) {
		  return CachedResourceService.make(
		      '/Kennel/:key',
		      {nimi: '@nimi',
		       kasvattaja_email: '@kasvattaja_email'},
		      localStorageService);
	      }])
    .factory('YhdistysPaimennustaipumusService', 
	     function ($resource) {
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
    .factory('TerveyskyselyService',
	     ['CachedResourceService', 'localStorageService',
	      function (CachedResourceService, localStorageService) {
		  return CachedResourceService.make(
		     "/TerveyskyselyTmp/:key",
		      {koira: '@koira',
		       koira_virallinen_nimi: '@koira_virallinen_nimi',
		       virallinen_lausunto_lonkka: '@virallinen_lausunto_lonkka',
		       virallinen_lausunto_kyynar: '@virallinen_lausunto_kyynar',
		       virallinen_lausunto_silma: '@virallinen_lausunto_silma',
		       virallinen_lausunto_muut: '@virallinen_lausunto_muut',
		       luusto_nivel_operoitu: '@luusto_nivel_operoitu',
		       luusto_nivel_operoitu_lisaselvitys: '@luusto_nivel_operoitu_lisaselvitys',
		       luusto_nivel_tutkittu: '@luusto_nivel_tutkittu',
		       luusto_nivel_tutkittu_lisaselvitys: '@luusto_nivel_tutkittu_lisaselvitys',
		       selkarankamuutokset: '@selkarankamuutokset',
		       selkarankamuutokset_lisaselvitys: '@selkarankamuutokset_lisaselvitys',
		       korvatulehdus: '@korvatulehdus',
		       virtsatietulehdus: '@virtsatietulehdus',
		       anaalirauhastulehdus: '@anaalirauhastulehdus',
		       eturauhastulehdus: '@eturauhastulehdus',
		       silmatulehdus: '@silmatulehdus',
		       suolistotulehdus: '@suolistotulehdus',
		       tulehtunut_rasvapatti: '@tulehtunut_rasvapatti',
		       kohtutulehdus: '@kohtutulehdus',
		       muu_tulehdus: '@muu_tulehdus',
		       tulehdussairaudet_lisaselvitys: '@tulehdussairaudet_lisaselvitys',
		       slo: '@slo',
		       imha: '@imha',
		       addison: '@addison',
		       kilpirauhasen_vajaatoiminta: '@kilpirauhasen_vajaatoiminta',
		       munuaisten_vajaatoiminta: '@munuaisten_vajaatoiminta',
		       haiman_vajaatoiminta: '@haiman_vajaatoiminta',
		       sle: '@sle',
		       itp: '@itp',
		       epilepsia: '@epilepsia',
		       sydanvika: '@sydanvika',
		       virtsakivet: '@virtsakivet',
		       cushing: '@cushing',
		       allergia: '@allergia',
		       diabetes: '@diabetes',
		       lihassurkastuma: '@lihassurkastuma',
		       muut_sairaudet_lisaselvitys: '@muut_sairaudet_lisaselvitys',
		       hyvanlaatuinen_kasvain: '@hyvanlaatuinen_kasvain',
		       hyvanlaatuinen_kasvain_lisaselvitys: '@hyvanlaatuinen_kasvain_lisaselvitys',
		       syopa: '@syopa',
		       syopa_lisaselvitys: '@syopa_lisaselvitys',
		       napatyra: '@napatyra',
		       napatyra_leikattu: '@napatyra_leikattu',
		       leikkaava_purenta: '@leikkaava_purenta',
		       tasapurenta: '@tasapurenta',
		       alapurenta: '@alapurenta',
		       ylapurenta: '@ylapurenta',
		       hammaspuutos_p1_p4: '@hammaspuutos_p1_p4',
		       hammaspuutos_etuhampaat: '@hammaspuutos_etuhampaat',
		       hammaspuutos_poskihampaat: '@hammaspuutos_poskihampaat',
		       liikahampaat: '@liikahampaat',
		       hammaspuutos_liikahammas_lisaselvitys: '@hammaspuutos_liikahammas_lisaselvitys',
		       kitalakeen_painuvat_kulmahampaat_pentuna: '@kitalakeen_painuvat_kulmahampaat_pentuna',
		       kitalakeen_painuvat_kulmahampaat_aikuisena: '@kitalakeen_painuvat_kulmahampaat_aikuisena',
		       kives_normaali: '@kives_normaali',
		       kives_toispuoleinen_puutos: '@kives_toispuoleinen_puutos',
		       kives_molemminpuolinen_puutos: '@kives_molemminpuolinen_puutos',
		       kives_hissikives: '@kives_hissikives',
		       kives_myohaan_laskeutunut: '@kives_myohaan_laskeutunut',
		       uros_astuminen: '@uros_astuminen',
		       uros_astuminen_helppo: '@uros_astuminen_helppo',
		       uros_astuminen_ongelmia: '@uros_astuminen_ongelmia',
		       uros_astuminen_lisaselvitys: '@uros_astuminen_lisaselvitys',
		       uros_jalkelaisia: '@uros_jalkelaisia',
		       uros_jalkelaisissa_sairauksia_vikoja: '@uros_jalkelaisissa_sairauksia_vikoja',
		       uros_jalkelaiset_lisaselvitys: '@uros_jalkelaiset_lisaselvitys',
		       narttu_valeraskauksia: '@narttu_valeraskauksia',
		       narttu_saannollinen_kiima: '@narttu_saannollinen_kiima',
		       narttu_kiimakierron_pituus: '@narttu_kiimakierron_pituus',
		       narttu_kaytetty_jalostukseen: '@narttu_kaytetty_jalostukseen',
		       narttu_ei_anna_astua: '@narttu_ei_anna_astua',
		       narttu_jaanyt_tyhjaksi: '@narttu_jaanyt_tyhjaksi',
		       narttu_raskaus_keskeytynyt: '@narttu_raskaus_keskeytynyt',
		       narttu_ei_hoida_pentuja_hyvin: '@narttu_ei_hoida_pentuja_hyvin',
		       narttu_jalostus_lisaselvitys: '@narttu_jalostus_lisaselvitys',
		       paukkuarka: '@paukkuarka',
		       aaniherkka: '@aaniherkka',
		       stressaa_helposti: '@stressaa_helposti',
		       aaniherkkyys_stressaus_lisaselvitys: '@aaniherkkyys_stressaus_lisaselvitys',
		       muut_pelot: '@muut_pelot',
		       muut_pelot_lisaselvitys: '@muut_pelot_lisaselvitys',
		       luonnetesti_lisaselvitys: '@luonnetesti_lisaselvitys',
		       muuta_huomioitavaa: '@muuta_huomioitavaa',
		       email: '@email'
		      },
		      localStorageService)
	      }])
    .factory('SidepanelService',
	     function () {
		 var state = {};
		 return {
		     get: function () { return state; },
		 };
	     })
    .factory('TypeaheadService',
	     ['$http', '$q', 'localStorageService',
	      function ($http, $q, localStorageService) {
		  function makeTypeahead (prefix) {
		      function typeahead(name) {
			  var cached = localStorageService.get(prefix + encodeURIComponent(name));
			  if (cached) {
			      var deferred = $q.defer();
			      deferred.resolve(cached);
			      return deferred.promise;
			  } else {
			      return $http.get(prefix + encodeURIComponent(name))
				  .then(function (response) { 
				      localStorageService.set(prefix + encodeURIComponent(name),
							      response.data);
				      return response.data 
				  });
			  }
		      }
		      return typeahead;
		  }
		  function clear () {
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
