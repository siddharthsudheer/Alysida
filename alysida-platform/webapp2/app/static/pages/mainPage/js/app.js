var app = angular.module('alysida', ['ngResource', 'ngAnimate', 'ngRoute', 'ui.date'])
    .config(['$routeProvider', function ($routeProvider) {
        $routeProvider
            .when('/', {
                templateUrl: 'pages/mainPage/views/blockchain.html',
                controller: 'BlockchainController'
            })
            .when('/transactions', {
                templateUrl: 'pages/mainPage/views/transactions.html',
                controller: 'TransactionsController'
            })
            .when('/add-transaction', {
                templateUrl: 'pages/mainPage/views/add-transaction.html',
                controller: 'AddTransactionController'
            });
    }]);


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

app.filter('reverse', function() {
    return function(items) {
      return items.slice().reverse();
    };
});

app.controller('MainController', function ($scope, $location, $rootScope, $http, $interval) {
    $scope.go = function ( path ) {
        $location.path( path );
    };

    $scope.location = $location.path();
    $scope.$on('$routeChangeSuccess', function (e) {
        $scope.location = $location.path();
    });
});

app.controller('PeersController', function ($scope, $http, socket) {
    $scope.peers = [];

    socket.emit('get_event', { endpoint: 'get-peer-addresses' });
    socket.on('get_event_resp', function (response) {
        $scope.$apply(function () {
            $scope.peers = response.data.peers;
        });
    });
});

app.controller('AddTransactionController', function ($scope, $location, socket) {
    $scope.txn = {
        sender: null,
        receiver: null,
        amount: null
    };
    $scope.submit = function() {
        if ($scope.form.$valid) {
            socket.emit('post_event', { endpoint: 'add-new-transaction', data: $scope.txn });
            socket.on('post_event_resp', function (response) {
                if (response.data == 'success') {
                    $scope.$apply(function () {
                        $scope.go( '/transactions' );
                    });
                };
                
                if (response.data == 'fail') {
                    console.log('fail');
                    alert(response.resp);
                }
            });
        }
    }


});

app.controller('TransactionsController', function ($scope, $http, socket) {
    $scope.txns = [];
    $scope.new_txns = [];
    $scope.loadingDone = false;
    $scope.selected_txns = {
        txn_hashes: []
    };

    socket.emit('get_event', { endpoint: 'get-unconfirmed-transactions' });
    socket.on('get_event_resp', function (response) {
        $scope.$apply(function () {
            $scope.txns = response.data.unconfirmed_txns;
            $scope.loadingDone = true;
        });
    });

    socket.on('accepted_new_txn', function (data) {
        $scope.$apply(function () {
            $scope.new_txns.push(data);
        });
    });

    $scope.mineBlock = function mineBlock() {
        if ($scope.selected_txns.txn_hashes.length > 0) {
            socket.emit('post_event', { endpoint: 'mine', data: $scope.selected_txns });
            socket.on('post_event_resp', function (response) {
                if (response.data == 'success') {
                    $scope.$apply(function () {
                        $scope.go( '/' );
                    });
                };
                
                if (response.data == 'fail') {
                    console.log('fail');
                    alert(response.resp);
                }
            });
        } else {
            alert('You need to select Unconfirmed Transactions.')
        }
    };

    $scope.toggleSelection = function toggleSelection(txnHash) {
        var idx = $scope.selected_txns.txn_hashes.indexOf(txnHash);

        // Is currently selected
        if (idx > -1) {
            $scope.selected_txns.txn_hashes.splice(idx, 1);
        }

        // Is newly selected
        else {
            $scope.selected_txns.txn_hashes.push(txnHash);
        }
    };


});

app.controller('BlockchainController', function ($scope, $http, socket) {
    $scope.blocks = [];
    $scope.loadingDone = false;
    socket.emit('get_event', { endpoint: 'get-blockchain' });
    socket.on('get_event_resp', function (response) {
        $scope.$apply(function () {
            $scope.blocks = response.data.blockchain.blocks;
            $scope.loadingDone = true;
        });
    });

    socket.on('accepted_new_block', function (data) {
        $scope.$apply(function () {
            $scope.blocks.push(data);
        });
    });
});





