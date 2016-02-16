'use strict';

describe('Service: SKService', function () {

  // load the service's module
  beforeEach(module('spiderKeeperApp'));

  // instantiate service
  var SKService;
  beforeEach(inject(function (_SKService_) {
    SKService = _SKService_;
  }));

  it('should do something', function () {
    expect(!!SKService).toBe(true);
  });

});
