"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.XML = void 0;
var XML = /** @class */ (function () {
    function XML(items) {
        this.items = items;
    }
    XML.prototype.toString = function () {
        var output = '<?xml version="1.0" encoding="UTF-8"?>\r\n<channels>\r\n';
        this.items.forEach(function (channel) {
            var logo = channel.logo ? " logo=\"".concat(channel.logo, "\"") : '';
            var xmltv_id = channel.xmltv_id || '';
            var lang = channel.lang || '';
            var site_id = channel.site_id || '';
            output += "  <channel site=\"".concat(channel.site, "\" lang=\"").concat(lang, "\" xmltv_id=\"").concat(escapeString(xmltv_id), "\" site_id=\"").concat(site_id, "\"").concat(logo, ">").concat(escapeString(channel.name), "</channel>\r\n");
        });
        output += '</channels>\r\n';
        return output;
    };
    return XML;
}());
exports.XML = XML;
function escapeString(value, defaultValue) {
    if (defaultValue === void 0) { defaultValue = ''; }
    if (!value)
        return defaultValue;
    var regex = new RegExp('((?:[\0-\x08\x0B\f\x0E-\x1F\uFFFD\uFFFE\uFFFF]|[\uD800-\uDBFF](?![\uDC00-\uDFFF])|(?:[^\uD800-\uDBFF]|^)[\uDC00-\uDFFF]))|([\\x7F-\\x84]|[\\x86-\\x9F]|[\\uFDD0-\\uFDEF]|(?:\\uD83F[\\uDFFE\\uDFFF])|(?:\\uD87F[\\uDF' +
        'FE\\uDFFF])|(?:\\uD8BF[\\uDFFE\\uDFFF])|(?:\\uD8FF[\\uDFFE\\uDFFF])|(?:\\uD93F[\\uDFFE\\uD' +
        'FFF])|(?:\\uD97F[\\uDFFE\\uDFFF])|(?:\\uD9BF[\\uDFFE\\uDFFF])|(?:\\uD9FF[\\uDFFE\\uDFFF])' +
        '|(?:\\uDA3F[\\uDFFE\\uDFFF])|(?:\\uDA7F[\\uDFFE\\uDFFF])|(?:\\uDABF[\\uDFFE\\uDFFF])|(?:\\' +
        'uDAFF[\\uDFFE\\uDFFF])|(?:\\uDB3F[\\uDFFE\\uDFFF])|(?:\\uDB7F[\\uDFFE\\uDFFF])|(?:\\uDBBF' +
        '[\\uDFFE\\uDFFF])|(?:\\uDBFF[\\uDFFE\\uDFFF])(?:[\\0-\\t\\x0B\\f\\x0E-\\u2027\\u202A-\\uD7FF\\' +
        'uE000-\\uFFFF]|[\\uD800-\\uDBFF][\\uDC00-\\uDFFF]|[\\uD800-\\uDBFF](?![\\uDC00-\\uDFFF])|' +
        '(?:[^\\uD800-\\uDBFF]|^)[\\uDC00-\\uDFFF]))', 'g');
    value = String(value || '').replace(regex, '');
    return value
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&apos;')
        .replace(/\n|\r/g, ' ')
        .replace(/  +/g, ' ')
        .trim();
}
