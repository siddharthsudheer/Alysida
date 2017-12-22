'use strict';

class Blockchain {
    /*@ngInject*/
    constructor($rootScope, $scope, $location, $state, $timeout) {
        this.$rootScope = $rootScope;
        this.$scope = $scope;
        this.$location = $location;
        this.$state = $state;
        this.$timeout = $timeout;
    }
}


angular
    .module('alysida')
    .component('blockchain', {
        controller: Blockchain,
        templateUrl: 'main/blockchain/blockchain.html'
    });
