var app = angular.module('alysida', [
'ngResource', 
'ngAnimate', 
'ngRoute', 
'ui-notification'
])
.config(['$routeProvider','NotificationProvider', function ($routeProvider, NotificationProvider) {
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
    NotificationProvider.setOptions({
        delay: 3000,
        startTop: 32,
        startRight: 16,
        verticalSpacing: 16,
        horizontalSpacing: 16,
        positionX: 'right',
        positionY: 'bottom',
        templateUrl: 'pages/mainPage/views/notification-template.html',
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

///////////////////////////////////////////////////////////////
//    CONTROLLERS
///////////////////////////////////////////////////////////////

app.controller('MainController', function ($rootScope, $timeout, $scope, $location, $rootScope, $http, $interval, Notification, socket) {
    $rootScope.loading_msg = '';
    $rootScope.mainLoading = false;
    $rootScope.newPeerFormOpen = false;
    $scope.menuReady = false;
    $timeout(function () {
        $scope.menuReady = true;
    },1000);
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

app.controller('PeersController', function ($filter, $timeout, $rootScope, $scope, $http, socket, Notification) {
    $scope.peers = [];

    $scope.peersReady = false;
    socket.emit('get_peers', { endpoint: 'get-peer-addresses' });
    socket.on('get_peers_resp', function (response) {
        $scope.peers = $filter('orderBy')(response.data.peers, 'status');
        $timeout(function () {
            $scope.peersReady = true;
        },500);
    });

    socket.on('new_peer_request', function (response) {
        var notifMsg = '<span class="reg">Received from : </span> \
                        <span class="ip">'+response.data.peer_ip+'</span>';
    
        Notification.info({title: 'New Peer Request', message: notifMsg});

        var new_peer = {
            peer_ip: response.data.peer_ip,
            status: response.data.status
        }
        socket.emit('get_peers', { endpoint: 'get-peer-addresses' });
    });

    socket.on('added_new_peer', function (response) {
        var notifMsg = '<span class="reg">Successfully added : </span> \
                        <span class="ip">'+response.data.ips+'</span> <br> \
                        <span class="status">Registration Status: Unregistered</span>';
        Notification.success({title: 'Added New Peer', message: notifMsg});
        socket.emit('get_peers', { endpoint: 'get-peer-addresses' });
    });

    socket.on('registered_with_new_peer', function (response) {
        var notifMsg = '<span class="reg">Registered with : </span> \
                        <span class="ip">'+response.data.peer_ip+'</span> <br> \
                        <span class="status">Approval Pending</span>';
        Notification.warning({title: 'Registered', message: notifMsg});
        var new_peer = {
            peer_ip: response.data.peer_ip,
            status: response.data.status
        }
        socket.emit('get_peers', { endpoint: 'get-peer-addresses' });
    });

    socket.on('registration_success_waiting_for_handshake', function (response) {
        var notifMsg = '<span class="reg">Registered with : </span> \
                        <span class="ip">'+response.data.peer_ip+'</span> <br> \
                        <span class="status">Success: Handshake Pending</span>';
        Notification.success({title: 'Successfully Registered', message: notifMsg});
        socket.emit('get_peers', { endpoint: 'get-peer-addresses' });
    });

    socket.on('registration_failed', function (response) {
        var notifMsg = '<span class="reg">Peer : </span> \
                        <span class="ip">'+response.data.peer_ip+'</span> <br> \
                        <span class="status">Check console for more info</span>';
        Notification.error({title: 'Failed Registration', message: notifMsg});
        socket.emit('get_peers', { endpoint: 'get-peer-addresses' });
    });

    socket.on('peer_not_reachable', function (response) {
        var notifMsg = '<span class="reg">Peer : </span> \
                        <span class="ip">'+response.data.peer_ip+'</span> <br> \
                        <span class="status">Unable to make contact with peer</span>';
        Notification.error({title: 'Peer Unreachable', message: notifMsg});
    });

    socket.on('accepted_peer', function (response) {
        var notifMsg = '<span class="reg">Connected With Peer : </span> \
                        <span class="ip">'+response.data.peer_ip+'</span> <br> \
                        <span class="status">Success</span>';
        Notification.success({title: 'Accepted Peer Request', message: notifMsg});
        socket.emit('get_peers', { endpoint: 'get-peer-addresses' });
    });

    socket.on('accepted_by_peer', function (response) {
        var notifMsg = '<span class="reg">Connected With Peer : </span> \
                        <span class="ip">'+response.data.peer_ip+'</span> <br> \
                        <span class="status">Success: Your request was accepted</span>';
        Notification.success({title: 'Peer Request Accepted', message: notifMsg});
        socket.emit('get_peers', { endpoint: 'get-peer-addresses' });
    });

    socket.on('yet_to_be_accepted_by_peer', function (response) {
        var notifMsg = '<span class="reg">Peer : </span> \
                        <span class="ip">'+response.data.peer_ip+'</span> <br> \
                        <span class="status">Peer is yet to accept your request</span>';
        Notification.warning({title: 'Request Approval Pending', message: notifMsg});
    });

    socket.on('new_peers_discovered', function (response) {
        var notifMsg = '<span class="reg">Found new peers using PeerDiscovery</span> \
                        <br> \
                        <span class="status">Success</span>';
        Notification.success({title: 'New Peers Found', message: notifMsg});
        socket.emit('get_peers', { endpoint: 'get-peer-addresses' });
        $timeout(function() { $rootScope.mainLoading = false;}, 1000);
    });

    socket.on('no_new_peers_discovered', function (response) {
        var notifMsg = '<span class="reg">No new peers discovered during PeerDiscovery</span> \
                        <br> \
                        <span class="status"></span>';
        Notification.info({title: 'No New Peers', message: notifMsg});
        socket.emit('get_peers', { endpoint: 'get-peer-addresses' });
        $timeout(function() { $rootScope.mainLoading = false;}, 1000);
    });

    //Actions
    $scope.acceptPeer = function acceptPeer(peer_ip) {
        $scope.peer_obj = {
            ips: []
        };
        $scope.peer_obj.ips.push(peer_ip);
        socket.emit('post_peers', { endpoint: 'accept-new-registration', data: $scope.peer_obj });
    };

    $scope.registerWithPeer = function registerPeer(peer_ip) {
        $scope.peer_obj = {
            peer_ip: []
        };
        $scope.peer_obj.peer_ip.push(peer_ip);
        socket.emit('post_peers', { endpoint: 'register-with-peer', data: $scope.peer_obj });
    };

    $scope.askPeerForUpdate = function askPeerForUpdate(peer_ip) {
        $scope.registerWithPeer(peer_ip);
    };


    // Manually adding Peers
    $scope.showNewPeerForm = function showNewPeerForm($event) {
        $event.stopPropagation();
        $rootScope.newPeerFormOpen = true;
    }

    $scope.addNewPeer = function addNewPeer($event, peer_ip) {
        $event.stopPropagation();
        var ips_obj = {
            ip: ""
        };
        ips_obj.ip = peer_ip;
        $rootScope.newPeerFormOpen = false;
        socket.emit('post_peers', { endpoint: 'add-peer-addresses', data: ips_obj });
    };

    $scope.closeNewPeerForm = function closeNewPeerForm($event) {
        $rootScope.newPeerFormOpen = false;
        $event.stopPropagation();
    };

    
});


app.controller('AddTransactionController', function ($rootScope, $scope, $location, socket, Notification) {
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

app.controller('TransactionsController', function ($timeout, $rootScope, $scope, $http, socket, Notification) {
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

app.controller('BlockchainController', function ($timeout, $rootScope, $scope, $http, socket, Notification) {
    $scope.blocks = [];
    $scope.loadingDone = false;
    socket.emit('get_event', { endpoint: 'get-blockchain' });
    socket.on('get_event_resp', function (response) {
        $scope.$apply(function () {
            $scope.blocks = response.data.blockchain.blocks;
            $timeout(function () {
                $scope.loadingDone = true;
            },1000);
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





