(function(){
    var app = angular.module('bookHotel',['ui.bootstrap']);
    app.config(function($interpolateProvider){
        $interpolateProvider.startSymbol('[[');
        $interpolateProvider.endSymbol(']]');
    })

    app

    .controller('hotelLoginController', function($http, $scope){
    	$scope.show_login_form = true;
    	$scope.signup = function(username, realname, password) {
    		console.log(username, realname, password)
    		data = {
    			'username': username,
    			'realname': realname,
    			'password': password
    		}
	    	$http.post("/api/users", data).success(function(data, status, headers) {
	            window.location = "/";
	        }).error(function(data, status, headers){
	            $scope.signup_error = data.error;
	        })
        };
        $scope.login = function(username, password) {
    		data = {
    			'username': username,
    			'password': password
    		}
	    	$http.post("/api/login", data).success(function(data, status, headers) {
	            window.location = "/";
	        }).error(function(data, status, headers){
	            $scope.login_error = data.error;
	        })
        };
    })

    .controller('hotelListingController', function($http, $scope){
    	$http.get('/api/get_token').success(function(data){
    		$scope.token = data.token
	    	$http.defaults.headers.common['Authorization'] = $scope.token;
	    	$scope.hotel_list = []
	    	$http.get('/api/hotels/').success(function(data){
	            $scope.hotel_list = data;
	            console.log(data);
	        });
    	});
    })

    .controller('hotelBookingListingController', function($http, $scope, $filter){
    	$http.get('/api/get_token').success(function(data){
    		$scope.token = data.token
	    	$http.defaults.headers.common['Authorization'] = $scope.token;
	    	$scope.booking_list = []
	    	$http.get('/api/bookings/').success(function(data){
	            $scope.booking_list = data;
	            console.log(data);
	        });
	    });

        $scope.cancel_booking = function(booking_id){
            $http.delete('/api/bookings/' + booking_id).success(function(data){
            	var booking_obj = ($filter('filter')($scope.booking_list, {id: booking_id[0][0] }))[0];
            	var booking_index = $scope.booking_list.indexOf(booking_obj);
            	console.log(booking_obj.id);
            	console.log(booking_index);
            	$scope.booking_list.splice(booking_index, 1);	
            });
        }

    })

    .controller('hotelViewController', function($http, $scope){
    	$scope.init = function(hotel_id) {
	    	$scope.hotel = {}
	    	$http.get('/api/hotels/'+hotel_id).success(function(data){
	            $scope.hotel = data.result;

	            // Update google map map
		        var address =  $scope.hotel.address + ',' + $scope.city + ',' + $scope.state + ',' + $scope.zipcode
		        $http.get('http://maps.google.com/maps/api/geocode/json?address='+address+'&sensor=false').success(function(mapData) {
					$scope.mapResult = mapData.results;
					if ($scope.mapResult.length != 0){
			      		angular.extend($scope, mapData);
			      		$scope.latitude = mapData.results[0].geometry.location.lat
			      		$scope.longitude = mapData.results[0].geometry.location.lng
			      	}
			    });

			    function initialize() {
			        var mapCanvas = document.getElementById('map');
			        var mapOptions = {
			          	center: new google.maps.LatLng($scope.latitude, $scope.longitude),
			          	zoom: 10,
			          	mapTypeId: google.maps.MapTypeId.ROADMAP
			        }
			        var map = new google.maps.Map(mapCanvas, mapOptions)
			    }
			    google.maps.event.addDomListener(window, 'load', initialize);
			});
        };
    })

    .controller('hotelBookingFormController', function($http, $scope){
    	$scope.init = function(hotel_id, user_id) {
    		$scope.user_id = user_id;
	    	$scope.hotel = {};
	    	$http.get('/api/get_token').success(function(data){
    			$scope.token = data.token;
	    		$http.defaults.headers.common['Authorization'] = $scope.token;
	    		$http.get('/api/hotels/'+hotel_id).success(function(data){
		            $scope.hotel = data.result;
	        	});
	        });
	    	$scope.formData = {};
	    	$scope.form_errors = {};
	    	$scope.preview = false;
            $scope.submitted = false;
        };

        $scope.dayDiff = function(firstDate,secondDate){
			var date2 = new Date($scope.formatString(secondDate));
			var date1 = new Date($scope.formatString(firstDate));
			var timeDiff = Math.abs(date2.getTime() - date1.getTime());   
			dayDifference = Math.ceil(timeDiff / (1000 * 3600 * 24));
			return dayDifference;
		};

		$scope.formatString = function(format) {
			var year   = parseInt(format.substring(0,4));
			var month  = parseInt(format.substring(5,7));
			var day   = parseInt(format.substring(8,10));
			var date = new Date(year, month-1, day);
			return date;
		};

		// dayDiff(firstDate,secondDate)

	    $scope.submit = function(isValid) {
            $scope.submitted = true;
            if (isValid) {
				$scope.preview = true;
				var day_diff = $scope.dayDiff($scope.formData.check_in, $scope.formData.check_out)
				$scope.total_cost = day_diff * $scope.formData.room_preference *$scope.hotel.nightly_rate
				return false
            }

	    };

	    $scope.postBooking = function() {
	    	$scope.booking = {
				'hotel_id': $scope.hotel.id,
				'user_id': $scope.user_id,
	        	'check_in': $scope.formData.check_in,
				'check_out': $scope.formData.check_out,
				'room_preference': $scope.formData.room_preference,
				'smoking_preference': true,
				'credit_card_number': $scope.formData.credit_card_number,
				'credit_card_name': $scope.formData.credit_card_name,
				'credit_card_expiry': $scope.formData.credit_card_expiry
	        }
	        var data = JSON.stringify($scope.booking);
	        $http.post("/api/bookings/", data).success(function(data, status, headers) {
	        	window.location = "/bookings";
	        }).error(function(data, status, headers){
	        	$scope.preview = false;
	        	console.log(data.error);
	        	$scope.form_error = data.error;
	        })
		};


    })

    .controller('ModalDemoCtrl', function($scope, $modal, $log){

          $scope.open = function () {

            var modalInstance = $modal.open({
              templateUrl: 'myModalContent.html',
              controller: 'ModalInstanceCtrl',
            });
          };
        })

    .controller('ModalInstanceCtrl', function($scope, $modalInstance, $http){ 
        $scope.password_changed=false;
        $scope.submitted=false;
		$scope.ok = function (isValid, password) {
			console.log(password);
			$scope.submitted=true;
			if (isValid) {
				$http.get('/api/get_token').success(function(data){
				$scope.token = data.token;
				$http.defaults.headers.common['Authorization'] = $scope.token;
					data = {'password': password}
			    	$http.post("/api/change_password", data).success(function(data, status, headers) {
			            $scope.password_changed=true;
			    	}).error(function(password, status, headers){
			        	console.log('COULDNT POST!');
			    	})
			    })
			};
		};

		$scope.cancel = function () {
			$modalInstance.dismiss('cancel');
		};
    })

	.controller('hotelCreateFormController', function($http, $scope){
    	$scope.init = function() {
	    	$http.get('/api/get_token').success(function(data){
    			$scope.token = data.token
	    		$http.defaults.headers.common['Authorization'] = $scope.token;
	        });
	    	$scope.formData = {};
	    	$scope.form_errors = {};
	    };

	    $scope.hotelCreate = function() {
	    	$scope.hotel = {
				'name': $scope.formData.name,
				'description': $scope.formData.description,
	        	'address': $scope.formData.address,
				'city': $scope.formData.city,
				'state': $scope.formData.state,
				'country': $scope.formData.country,
				'zipcode': $scope.formData.zipcode,
				'nightly_rate': $scope.formData.nightly_rate,
	        }
	        var data = JSON.stringify($scope.hotel);
	        $http.post("/api/hotels/", data).success(function(data, status, headers) {
	        	window.location = "/";
	        }).error(function(data, status, headers){
	        	$scope.preview = false;
	        	console.log(data.error);
	        	$scope.form_error = data.error;
	        })
		};
    })
})();