'use strict';

describe('Controller: DashspiderCtrl', function () {

  // load the controller's module
  beforeEach(module('spiderKeeperApp'));

  var DashspiderCtrl,
    scope;

  // Initialize the controller and a mock scope
  beforeEach(inject(function ($controller, $rootScope) {
    scope = $rootScope.$new();
    DashspiderCtrl = $controller('DashspiderCtrl', {
      $scope: scope
      // place here mocked dependencies
    });
  }));

  it('should attach a list of awesomeThings to the scope', function () {
    expect(DashspiderCtrl.awesomeThings.length).toBe(3);
  });
});
