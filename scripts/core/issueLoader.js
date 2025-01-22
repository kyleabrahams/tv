"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __generator = (this && this.__generator) || function (thisArg, body) {
    var _ = { label: 0, sent: function() { if (t[0] & 1) throw t[1]; return t[1]; }, trys: [], ops: [] }, f, y, t, g = Object.create((typeof Iterator === "function" ? Iterator : Object).prototype);
    return g.next = verb(0), g["throw"] = verb(1), g["return"] = verb(2), typeof Symbol === "function" && (g[Symbol.iterator] = function() { return this; }), g;
    function verb(n) { return function (v) { return step([n, v]); }; }
    function step(op) {
        if (f) throw new TypeError("Generator is already executing.");
        while (g && (g = 0, op[0] && (_ = 0)), _) try {
            if (f = 1, y && (t = op[0] & 2 ? y["return"] : op[0] ? y["throw"] || ((t = y["return"]) && t.call(y), 0) : y.next) && !(t = t.call(y, op[1])).done) return t;
            if (y = 0, t) op = [op[0] & 2, t.value];
            switch (op[0]) {
                case 0: case 1: t = op; break;
                case 4: _.label++; return { value: op[1], done: false };
                case 5: _.label++; y = op[1]; op = [0]; continue;
                case 7: op = _.ops.pop(); _.trys.pop(); continue;
                default:
                    if (!(t = _.trys, t = t.length > 0 && t[t.length - 1]) && (op[0] === 6 || op[0] === 2)) { _ = 0; continue; }
                    if (op[0] === 3 && (!t || (op[1] > t[0] && op[1] < t[3]))) { _.label = op[1]; break; }
                    if (op[0] === 6 && _.label < t[1]) { _.label = t[1]; t = op; break; }
                    if (t && _.label < t[2]) { _.label = t[2]; _.ops.push(op); break; }
                    if (t[2]) _.ops.pop();
                    _.trys.pop(); continue;
            }
            op = body.call(thisArg, _);
        } catch (e) { op = [6, e]; y = 0; } finally { f = t = 0; }
        if (op[0] & 5) throw op[1]; return { value: op[0] ? op[1] : void 0, done: true };
    }
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.IssueLoader = void 0;
var core_1 = require("@freearhey/core");
var plugin_rest_endpoint_methods_1 = require("@octokit/plugin-rest-endpoint-methods");
var plugin_paginate_rest_1 = require("@octokit/plugin-paginate-rest");
var core_2 = require("@octokit/core");
var _1 = require("./");
var constants_1 = require("../constants");
var CustomOctokit = core_2.Octokit.plugin(plugin_paginate_rest_1.paginateRest, plugin_rest_endpoint_methods_1.restEndpointMethods);
var octokit = new CustomOctokit();
var IssueLoader = /** @class */ (function () {
    function IssueLoader() {
    }
    IssueLoader.prototype.load = function (_a) {
        return __awaiter(this, arguments, void 0, function (_b) {
            var issues, _c, parser;
            var labels = _b.labels;
            return __generator(this, function (_d) {
                switch (_d.label) {
                    case 0:
                        labels = Array.isArray(labels) ? labels.join(',') : labels;
                        issues = [];
                        if (!constants_1.TESTING) return [3 /*break*/, 6];
                        _c = labels;
                        switch (_c) {
                            case 'broken guide,status:warning': return [3 /*break*/, 1];
                            case 'broken guide,status:down': return [3 /*break*/, 3];
                        }
                        return [3 /*break*/, 5];
                    case 1: return [4 /*yield*/, Promise.resolve().then(function () { return require('../../tests/__data__/input/issues/broken_guide_warning.mjs'); })];
                    case 2:
                        issues = (_d.sent())
                            .default;
                        return [3 /*break*/, 5];
                    case 3: return [4 /*yield*/, Promise.resolve().then(function () { return require('../../tests/__data__/input/issues/broken_guide_down.mjs'); })];
                    case 4:
                        issues = (_d.sent()).default;
                        return [3 /*break*/, 5];
                    case 5: return [3 /*break*/, 8];
                    case 6: return [4 /*yield*/, octokit.paginate(octokit.rest.issues.listForRepo, {
                            owner: constants_1.OWNER,
                            repo: constants_1.REPO,
                            per_page: 100,
                            labels: labels,
                            headers: {
                                'X-GitHub-Api-Version': '2022-11-28'
                            }
                        })];
                    case 7:
                        issues = _d.sent();
                        _d.label = 8;
                    case 8:
                        parser = new _1.IssueParser();
                        return [2 /*return*/, new core_1.Collection(issues).map(parser.parse)];
                }
            });
        });
    };
    return IssueLoader;
}());
exports.IssueLoader = IssueLoader;
