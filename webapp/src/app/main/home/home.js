'use strict';

angular.module('alysida')
.config($stateProvider => {
    $stateProvider
        .state('main.home', {
            url: '',
            template: `<home></home>`
        }
    )
});
