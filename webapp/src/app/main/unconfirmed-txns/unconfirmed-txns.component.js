'use strict';

class UnconfirmedTxns {
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
    .component('unconfirmedTxns', {
        controller: UnconfirmedTxns,
        templateUrl: 'main/unconfirmed-txns/unconfirmed-txns.component.html'
    });
