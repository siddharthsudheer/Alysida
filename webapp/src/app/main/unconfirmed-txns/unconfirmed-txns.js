'use strict';

angular.module('alysida')
.config($stateProvider => {
    $stateProvider
        .state('main.unconfirmed-txns', {
            url: '',
            template: `<unconfirmed-txns></unconfirmed-txns>`
        }
    )
});
