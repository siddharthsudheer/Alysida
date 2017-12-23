'use strict';

class Home {
    /*@ngInject*/
    constructor($rootScope, $scope, $location, $state, $timeout) {
        this.$rootScope = $rootScope;
        this.$scope = $scope;
        this.$location = $location;
        this.$state = $state;
        this.$timeout = $timeout;

        this.txn = {
            sender: null,
            receiver: null,
            amount: null
        };
    }
}


angular
    .module('alysida')
    .component('home', {
        controller: Home,
        templateUrl: 'main/home/home.component.html'
    });
