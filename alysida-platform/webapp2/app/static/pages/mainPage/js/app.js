// Declare app level module which depends on filters, and services
var app = angular.module('flaskSPA', ['ngResource', 'ngAnimate', 'ngRoute', 'ui.bootstrap', 'ui.date', 'pageslide-directive'])
    .config(['$routeProvider', function ($routeProvider) {
        $routeProvider
            .when('/', {
                templateUrl: 'pages/mainPage/views/dashboard.html'
            })
            .when('/transactions', {
                templateUrl: 'pages/mainPage/views/transactions.html',
                controller: 'TransactionsController'
            })
            .when('/example-customer', {
                templateUrl: 'pages/mainPage/views/example-customer.html',
                controller: 'IndexController'
            });
    }]);

// app.factory('socket', function ($rootScope) {
//     var socket = io.connect();
//     return {
//         on: function (eventName, callback) {
//             socket.on(eventName, function () {
//                 var args = arguments;
//                 $rootScope.$apply(function () {
//                     callback.apply(socket, args);
//                 });
//             });
//         },
//         emit: function (eventName, data, callback) {
//             socket.emit(eventName, data, function () {
//                 var args = arguments;
//                 $rootScope.$apply(function () {
//                     if (callback) {
//                         callback.apply(socket, args);
//                     }
//                 });
//             })
//         }
//     };
// });

app.factory('socket', ['$rootScope', function ($rootScope) {
    var namespace = '/test';
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace);

    return {
        on: function (eventName, callback) {
            console.log('on');
            socket.on(eventName, callback);
        },
        emit: function (eventName, data) {
            console.log('emit');
            socket.emit(eventName, data);
        }
    };
}]);

app.controller('SiteArbiter', function ($scope, $location, $rootScope, $http, $interval) {
    $scope.location = $location.path();
    $scope.$on('$routeChangeSuccess', function (e) {
        $scope.location = $location.path();
    })
});

app.controller('IndexController', function ($scope, socket) {
    $scope.newCustomers = [];
    $scope.currentCustomer = {};

    $scope.join = function () {
        socket.emit('add-customer', $scope.currentCustomer);
    };

    socket.on('notification', function (data) {
        $scope.$apply(function () {
            $scope.newCustomers.push(data.customer);
        });
    });
});

app.controller('TransactionsController', function ($scope, $http, socket) {
    $scope.txns = [];
    $scope.new_txns = [];

    socket.emit('get_event', {endpoint: 'get-unconfirmed-transactions'});
    socket.on('get_event_resp', function (response) {
        $scope.$apply(function () {
            $scope.txns = response.data.unconfirmed_txns;
        });
    });

    socket.on('accepted_new_txn', function (data) {
        $scope.$apply(function () {
            $scope.new_txns.push(data);
        });
    });
});





