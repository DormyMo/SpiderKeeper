'use strict';

describe('Controller: DashschdulerCtrl', function () {

  // load the controller's module
  beforeEach(module('spiderKeeperApp'));

  var DashschdulerCtrl,
    scope;

  // Initialize the controller and a mock scope
  beforeEach(inject(function ($controller, $rootScope) {
    scope = $rootScope.$new();
    DashschdulerCtrl = $controller('DashschdulerCtrl', {
      $scope: scope
      // place here mocked dependencies
    });
  }));

  it('should attach a list of awesomeThings to the scope', function () {
    expect(DashschdulerCtrl.awesomeThings.length).toBe(3);
  });
});
