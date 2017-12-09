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
            socket.on(eventName, callback);
        },
        emit: function (eventName, data) {
            socket.emit(eventName, data);
        }
    };
}]);

app.filter('reverse', function() {
    return function(items) {
      return items.slice().reverse();
    };
});

app.controller('MainController', function ($rootScope, $timeout, $scope, $location, $rootScope, $http, $interval, socket) {
    $rootScope.loading_msg = '';
    $rootScope.mainLoading = false;
    $scope.go = function ( path ) {
        $location.path( path );
    };

    $scope.location = $location.path();
    $scope.$on('$routeChangeSuccess', function (e) {
        $scope.location = $location.path();
    });

    $scope.doConsensus = function doConsensus() {
        $rootScope.loading_msg = 'Finding Consensus Among Peers...';
        $rootScope.mainLoading = true;
        console.log('Finding Consensus Among Peers...');
        socket.emit('do_consensus', { endpoint: 'consensus' });
    };
    socket.on('do_consensus_resp', function (response) {
        console.log('done consensus');
        $scope.$apply(function () {
            $timeout(function() { $rootScope.mainLoading = false;}, 1000);
            socket.emit('get_event', { endpoint: 'get-blockchain' });
            $scope.go( '/' );
        });
    });

    $scope.discoverPeers = function discoverPeers() {
        $rootScope.loading_msg = 'Discovering Peers...';
        $rootScope.mainLoading = true;
        console.log('Discovering Peers...');
        socket.emit('get_peers', { endpoint: 'discover-peer-addresses' });
    };
});

app.controller('PeersController', function ($timeout, $rootScope, $scope, $http, socket) {
    $scope.peers = [];

    socket.emit('get_peers', { endpoint: 'get-peer-addresses' });
    socket.on('get_peers_resp', function (response) {
        // if ($scope.peers > 0) {
        //     var response_peers = response.data.peers;
        //     for (var i; i < response_peers.length; i++) {
        //         if ()
        //     }
        // } else {
        //     $scope.$apply(function () {
        //         $scope.peers = response.data.peers;
        //     });
        // }

        $scope.$apply(function () {
            $scope.peers = response.data.peers;
        });
    });

    socket.on('new_peer', function (data) {
        socket.emit('get_peers', { endpoint: 'get-peer-addresses' });
    });

    socket.on('peer_discovery_result', function (data) {
        $timeout(function() { $rootScope.mainLoading = false;}, 1000);
        if (data.difference != 'No Difference.') {
            socket.emit('get_peers', { endpoint: 'get-peer-addresses' });
            console.log(data);
        }
    });

    $scope.acceptPeer = function acceptPeer(peer_ip) {
        $scope.peer_obj = {
            ips: []
        };
        $scope.peer_obj.ips.push(peer_ip);
        socket.emit('post_peers', { endpoint: 'accept-new-registration', data: $scope.peer_obj });
        socket.on('post_peers_resp', function (response) {
            if (response.data == 'success') {
                socket.emit('get_peers', { endpoint: 'get-peer-addresses' });
            };
            
            if (response.data == 'fail') {
                console.log('fail');
                alert(response.resp);
            }
            
        });
    };

    $scope.registerWithPeer = function registerPeer(peer_ip) {
        socket.emit('get_peers', { endpoint: 'register-me' });
    };

    $scope.askPeerForUpdate = function askPeerForUpdate(peer_ip) {
        $scope.peer_obj = {
            ip: ''
        };
        $scope.peer_obj.ip = peer_ip;
        socket.emit('post_peers', { endpoint: 'accept-new-registration', data: $scope.peer_obj });
        socket.on('post_peers_resp', function (response) {
            if (response.data == 'success') {
                socket.emit('get_peers', { endpoint: 'get-peer-addresses' });
            };
            
            if (response.data == 'fail') {
                console.log('fail');
                alert(response.resp);
            }
            
        });
    };

    $scope.askPeerForUpdate = function askPeerForUpdate(peer_ip) {
        socket.emit('get_peers', { endpoint: 'register-me' });
    };
});

app.controller('AddTransactionController', function ($rootScope, $scope, $location, socket) {
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

app.controller('TransactionsController', function ($timeout, $rootScope, $scope, $http, socket) {
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
            socket.emit('get_event', { endpoint: 'get-unconfirmed-transactions' });
            // $scope.new_txns.push(data);
        });
    });

    $scope.mineBlock = function mineBlock() {
        if ($scope.selected_txns.txn_hashes.length > 0) {
            $rootScope.loading_msg = 'Mining Block...';
            console.log('Mining Block...');
            $rootScope.mainLoading = true;
            socket.emit('post_event', { endpoint: 'mine', data: $scope.selected_txns });
            socket.on('post_event_resp', function (response) {
                if (response.data == 'success') {
                    $timeout(function() { $rootScope.mainLoading = false;}, 1000);
                    $scope.$apply(function () {
                        $scope.go( '/' );
                    });
                };
                
                if (response.data == 'fail') {
                    $rootScope.mainLoading = false;
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

app.controller('BlockchainController', function ($rootScope, $scope, $http, socket) {
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
        socket.emit('do_consensus', { endpoint: 'consensus' });
        $scope.$apply(function () {
            // $scope.blocks.push(data);
            socket.emit('get_event', { endpoint: 'get-blockchain' });
        });
    });
});





