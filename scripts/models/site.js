"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.Site = void 0;
var StatusCode;
(function (StatusCode) {
    StatusCode["DOWN"] = "down";
    StatusCode["WARNING"] = "warning";
    StatusCode["OK"] = "ok";
})(StatusCode || (StatusCode = {}));
var Site = /** @class */ (function () {
    function Site(_a) {
        var domain = _a.domain, issues = _a.issues;
        this.domain = domain;
        this.issues = issues;
    }
    Site.prototype.getStatus = function () {
        var issuesWithStatusDown = this.issues.filter(function (issue) {
            return issue.labels.find(function (label) { return label === 'status:down'; });
        });
        if (issuesWithStatusDown.notEmpty())
            return {
                code: StatusCode.DOWN,
                emoji: '🔴'
            };
        var issuesWithStatusWarning = this.issues.filter(function (issue) {
            return issue.labels.find(function (label) { return label === 'status:warning'; });
        });
        if (issuesWithStatusWarning.notEmpty())
            return {
                code: StatusCode.WARNING,
                emoji: '🟡'
            };
        return {
            code: StatusCode.OK,
            emoji: '🟢'
        };
    };
    Site.prototype.getIssues = function () {
        return this.issues.map(function (issue) { return issue.getURL(); });
    };
    return Site;
}());
exports.Site = Site;
