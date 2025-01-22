"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.IssueParser = void 0;
var core_1 = require("@freearhey/core");
var models_1 = require("../models");
var FIELDS = new core_1.Dictionary({
    Site: 'site'
});
var IssueParser = /** @class */ (function () {
    function IssueParser() {
    }
    IssueParser.prototype.parse = function (issue) {
        var fields = issue.body.split('###');
        var data = new core_1.Dictionary();
        fields.forEach(function (field) {
            var parsed = field.split(/\r?\n/).filter(Boolean);
            var _label = parsed.shift();
            _label = _label ? _label.trim() : '';
            var _value = parsed.join('\r\n');
            _value = _value ? _value.trim() : '';
            if (!_label || !_value)
                return data;
            var id = FIELDS.get(_label);
            var value = _value === '_No response_' || _value === 'None' ? '' : _value;
            if (!id)
                return;
            data.set(id, value);
        });
        var labels = issue.labels.map(function (label) { return label.name; });
        return new models_1.Issue({ number: issue.number, labels: labels, data: data });
    };
    return IssueParser;
}());
exports.IssueParser = IssueParser;
