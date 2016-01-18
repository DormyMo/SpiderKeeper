/**
 * Created by modm on 15/12/9.
 */
(function() {
  'use strict';

  var module = angular.module('initMaterial', []);

  var inputElements = [
    'input',
    'textarea',
    'select'
  ];

  var inputDirective = [function() {
    return {
      restrict: 'E',
      link: function($scope, $element) {
        if ($element.hasClass('form-control')) {
          $.material.input($element);
        } else {
          var type = $element.attr('type');
          var func = $.material[type];
          if (typeof(func) === 'function') {
            func($element);
          }
        }
      }
    };
  }];

  for (var i = 0; i < inputElements.length; i++) {
    module.directive(inputElements[i], inputDirective);
  }


  var ripplesDirective = [function() {
    return {
      restrict: 'C',
      link: function($scope, $element) {
        if ($element.hasClass('withoutripple') || $element.hasClass('btn-link')) {
          return;
        }
        $.material.ripples($element);
      }
    };
  }];

  module.directive('withRipples', ripplesDirective);
  module.directive('withripple', ripplesDirective);
  module.directive('cardImage', ripplesDirective);
  module.directive('btn', ripplesDirective);
  module.directive('input', ripplesDirective);

})();
