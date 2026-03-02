"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.Issue = void 0;
var constants_1 = require("../constants");
var Issue = /** @class */ (function () {
    function Issue(_a) {
        var number = _a.number, labels = _a.labels, data = _a.data;
        this.number = number;
        this.labels = labels;
        this.data = data;
    }
    Issue.prototype.getURL = function () {
        return "https://github.com/".concat(constants_1.OWNER, "/").concat(constants_1.REPO, "/issues/").concat(this.number);
    };
    return Issue;
}());
exports.Issue = Issue;
