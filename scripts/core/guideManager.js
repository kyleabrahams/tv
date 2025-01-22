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
exports.GuideManager = void 0;
var core_1 = require("@freearhey/core");
var _1 = require(".");
var GuideManager = /** @class */ (function () {
    function GuideManager(_a) {
        var channels = _a.channels, programs = _a.programs, logger = _a.logger, options = _a.options;
        this.options = options;
        this.logger = logger;
        this.channels = channels;
        this.programs = programs;
        this.storage = new core_1.Storage();
    }
    GuideManager.prototype.createGuides = function () {
        return __awaiter(this, void 0, void 0, function () {
            var pathTemplate, groupedChannels, groupedPrograms, _i, _a, groupKey, guide;
            return __generator(this, function (_b) {
                switch (_b.label) {
                    case 0:
                        pathTemplate = new core_1.StringTemplate(this.options.output);
                        groupedChannels = this.channels
                            .orderBy([function (channel) { return channel.xmltv_id; }])
                            .uniqBy(function (channel) { return "".concat(channel.xmltv_id, ":").concat(channel.site, ":").concat(channel.lang); })
                            .groupBy(function (channel) {
                            return pathTemplate.format({ lang: channel.lang || 'en', site: channel.site || '' });
                        });
                        groupedPrograms = this.programs
                            .orderBy([function (program) { return program.channel; }, function (program) { return program.start; }])
                            .groupBy(function (program) {
                            var lang = program.titles && program.titles.length && program.titles[0].lang
                                ? program.titles[0].lang
                                : 'en';
                            return pathTemplate.format({ lang: lang, site: program.site || '' });
                        });
                        _i = 0, _a = groupedPrograms.keys();
                        _b.label = 1;
                    case 1:
                        if (!(_i < _a.length)) return [3 /*break*/, 4];
                        groupKey = _a[_i];
                        guide = new _1.Guide({
                            filepath: groupKey,
                            gzip: this.options.gzip,
                            channels: new core_1.Collection(groupedChannels.get(groupKey)),
                            programs: new core_1.Collection(groupedPrograms.get(groupKey)),
                            logger: this.logger
                        });
                        return [4 /*yield*/, guide.save()];
                    case 2:
                        _b.sent();
                        _b.label = 3;
                    case 3:
                        _i++;
                        return [3 /*break*/, 1];
                    case 4: return [2 /*return*/];
                }
            });
        });
    };
    return GuideManager;
}());
exports.GuideManager = GuideManager;
