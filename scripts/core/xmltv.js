"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.XMLTV = void 0;
var epg_grabber_1 = require("epg-grabber");
var XMLTV = /** @class */ (function () {
    function XMLTV(_a) {
        var channels = _a.channels, programs = _a.programs, date = _a.date;
        this.channels = channels;
        this.programs = programs;
        this.date = date;
    }
    XMLTV.prototype.toString = function () {
        return (0, epg_grabber_1.generateXMLTV)({
            channels: this.channels.all(),
            programs: this.programs.all(),
            date: this.date.toJSON()
        });
    };
    return XMLTV;
}());
exports.XMLTV = XMLTV;
