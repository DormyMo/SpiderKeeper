'use strict';

describe('Service: scrapydApi', function () {

  // load the service's module
  beforeEach(module('spiderKeeperApp'));

  // instantiate service
  var scrapydApi;
  beforeEach(inject(function (_scrapydApi_) {
    scrapydApi = _scrapydApi_;
  }));

  it('should do something', function () {
    expect(!!scrapydApi).toBe(true);
  });

});
