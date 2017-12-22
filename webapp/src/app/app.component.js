'use strict';

class App {
  /*@ngInject*/
  constructor($state, $timeout) {
    this.$timeout = $timeout;
    this.$state = $state;
    this.defaultState = 'main.blockchain';
  }

  goToMain() {
    return this.$state.go(this.defaultState);
  }
}

angular
  .module('alysida')
  .component('app', {
    controller: App,
    controllerAs: '$appCtrl',
    template: `<div ui-view=""></div>`
  });
