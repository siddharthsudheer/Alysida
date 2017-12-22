'use strict';

angular.module('alysida', [
  'ui.router',
  'ngAnimate',
  'ngResource',
  'ui-notification'
])

/*@ngInject*/
.config(function ($urlRouterProvider, $locationProvider, $httpProvider, $stateProvider, $urlMatcherFactoryProvider, NotificationProvider) {
    $urlMatcherFactoryProvider.strictMode(false)
	$locationProvider.html5Mode(true);
	$httpProvider.useApplyAsync(true);
    $urlRouterProvider.otherwise('/');
    
    // NotificationProvider.setOptions({
    //     delay: 3000,
    //     startTop: 32,
    //     startRight: 16,
    //     verticalSpacing: 16,
    //     horizontalSpacing: 16,
    //     positionX: 'right',
    //     positionY: 'bottom',
    //     templateUrl: 'pages/mainPage/views/notification-template.html',
    // });
});

