'use strict';

class Main {
    /*@ngInject*/
    constructor($rootScope, $scope, $location, $state, $timeout, $document, $window) {
        this.$rootScope = $rootScope;
        this.$scope = $scope;
        this.$location = $location;
        this.$state = $state;
        this.$timeout = $timeout;
        this.$document = $document;
        this.showHeader = false;
    }


}

angular
    .module('alysida')
    .component('main', {
        controller: Main,
        controllerAs: '$mainCtrl',
        templateUrl: 'main/main.html'
    });
