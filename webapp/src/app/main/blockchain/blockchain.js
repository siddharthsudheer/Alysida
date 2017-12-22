'use strict';

angular.module('alysida')
.config($stateProvider => {
    $stateProvider
        .state('main.blockchain', {
            url: '',
            template: `<blockchain></blockchain>`
        }
    )
});
