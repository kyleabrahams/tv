"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.Queue = void 0;
var core_1 = require("@freearhey/core");
var Queue = /** @class */ (function () {
    function Queue() {
        this._data = new core_1.Dictionary();
    }
    Queue.prototype.missing = function (key) {
        return this._data.missing(key);
    };
    Queue.prototype.add = function (key, _a) {
        var channel = _a.channel, config = _a.config, date = _a.date;
        this._data.set(key, {
            channel: channel,
            date: date,
            config: config,
            error: null
        });
    };
    Queue.prototype.size = function () {
        return Object.values(this._data.data()).length;
    };
    Queue.prototype.items = function () {
        return Object.values(this._data.data());
    };
    Queue.prototype.isEmpty = function () {
        return this.size() === 0;
    };
    return Queue;
}());
exports.Queue = Queue;
