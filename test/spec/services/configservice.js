'use strict';

describe('Service: configService', function () {

  // load the service's module
  beforeEach(module('spiderKeeperApp'));

  // instantiate service
  var configService;
  beforeEach(inject(function (_configService_) {
    configService = _configService_;
  }));

  it('should do something', function () {
    expect(!!configService).toBe(true);
  });

});
