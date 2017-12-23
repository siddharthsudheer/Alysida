'use strict';

class BottomNav {
    /*@ngInject*/
    constructor($rootScope, $scope, $location, $state, $timeout, $document, $window) {
        this.$rootScope = $rootScope;
        this.$scope = $scope;
        this.$location = $location;
        this.$state = $state;
        this.$timeout = $timeout;
        this.$document = $document;
    }


}

angular
    .module('alysida')
    .component('bottomNav', {
        controller: BottomNav,
        controllerAs: '$bottomNav',
        templateUrl: 'components/bottom-nav/bottom-nav.component.html'
    });
