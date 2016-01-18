'use strict';

describe('Controller: DashjobCtrl', function () {

  // load the controller's module
  beforeEach(module('spiderKeeperApp'));

  var DashjobCtrl,
    scope;

  // Initialize the controller and a mock scope
  beforeEach(inject(function ($controller, $rootScope) {
    scope = $rootScope.$new();
    DashjobCtrl = $controller('DashjobCtrl', {
      $scope: scope
      // place here mocked dependencies
    });
  }));

  it('should attach a list of awesomeThings to the scope', function () {
    expect(DashjobCtrl.awesomeThings.length).toBe(3);
  });
});
