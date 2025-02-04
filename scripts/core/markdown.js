"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.Markdown = void 0;
var markdown_include_1 = require("markdown-include");
var Markdown = /** @class */ (function () {
    function Markdown(filepath) {
        this.filepath = filepath;
    }
    Markdown.prototype.compile = function () {
        markdown_include_1.default.compileFiles(this.filepath);
    };
    return Markdown;
}());
exports.Markdown = Markdown;
