'use strict';

describe('Directive: btnUpload', function () {

  // load the directive's module
  beforeEach(module('spiderKeeperApp'));

  var element,
    scope;

  beforeEach(inject(function ($rootScope) {
    scope = $rootScope.$new();
  }));

  it('should make hidden element visible', inject(function ($compile) {
    element = angular.element('<btn-upload></btn-upload>');
    element = $compile(element)(scope);
    expect(element.text()).toBe('this is the btnUpload directive');
  }));
});
