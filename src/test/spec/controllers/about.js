'use strict';

describe('Controller: AboutCtrl', function () {

  // load the controller's module
  beforeEach(module('spiderKeeperApp'));

  var AboutCtrl,
    scope;

  // Initialize the controller and a mock scope
  beforeEach(inject(function ($controller, $rootScope) {
    scope = $rootScope.$new();
    AboutCtrl = $controller('AboutCtrl', {
      $scope: scope
      // place here mocked dependencies
    });
  }));

  it('should attach a list of awesomeThings to the scope', function () {
    expect(AboutCtrl.awesomeThings.length).toBe(3);
  });
});
