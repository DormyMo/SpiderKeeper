'use strict';

describe('Filter: dateformat', function () {

  // load the filter's module
  beforeEach(module('spiderKeeperApp'));

  // initialize a new instance of the filter before each test
  var dateformat;
  beforeEach(inject(function ($filter) {
    dateformat = $filter('dateformat');
  }));

  it('should return the input prefixed with "dateformat filter:"', function () {
    var text = 'angularjs';
    expect(dateformat(text)).toBe('dateformat filter: ' + text);
  });

});
