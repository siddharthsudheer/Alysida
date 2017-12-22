'use strict';

angular.module('alysida')
.config($stateProvider => {
    $stateProvider
        .state('main', {
            url: '/',
            abstract: true,
            template: `<main></main>`
        }
    )
});