"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.HTMLTable = void 0;
var HTMLTable = /** @class */ (function () {
    function HTMLTable(data, columns) {
        this.data = data;
        this.columns = columns;
    }
    HTMLTable.prototype.toString = function () {
        var output = '<table>\r\n';
        output += '  <thead>\r\n    <tr>';
        for (var _i = 0, _a = this.columns; _i < _a.length; _i++) {
            var column = _a[_i];
            output += "<th align=\"left\">".concat(column.name, "</th>");
        }
        output += '</tr>\r\n  </thead>\r\n';
        output += '  <tbody>\r\n';
        for (var _b = 0, _c = this.data; _b < _c.length; _b++) {
            var item = _c[_b];
            output += '    <tr>';
            var i = 0;
            for (var prop in item) {
                var column = this.columns[i];
                var nowrap = column.nowrap ? ' nowrap' : '';
                var align = column.align ? " align=\"".concat(column.align, "\"") : '';
                output += "<td".concat(align).concat(nowrap, ">").concat(item[prop], "</td>");
                i++;
            }
            output += '</tr>\r\n';
        }
        output += '  </tbody>\r\n';
        output += '</table>';
        return output;
    };
    return HTMLTable;
}());
exports.HTMLTable = HTMLTable;
