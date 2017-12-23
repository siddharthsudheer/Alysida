'use strict';

class TopNav {
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
    .component('topNav', {
        controller: TopNav,
        controllerAs: '$topNav',
        templateUrl: 'components/top-nav/top-nav.component.html'
    });
