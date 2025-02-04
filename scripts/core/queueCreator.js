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
exports.QueueCreator = void 0;
var core_1 = require("@freearhey/core");
var _1 = require("./");
var constants_1 = require("../constants");
var path_1 = require("path");
var QueueCreator = /** @class */ (function () {
    function QueueCreator(_a) {
        var parsedChannels = _a.parsedChannels, logger = _a.logger, options = _a.options;
        this.parsedChannels = parsedChannels;
        this.logger = logger;
        this.sitesStorage = new core_1.Storage();
        this.dataStorage = new core_1.Storage(constants_1.DATA_DIR);
        this.parser = new _1.ChannelsParser({ storage: new core_1.Storage() });
        this.options = options;
        this.configLoader = new _1.ConfigLoader();
    }
    QueueCreator.prototype.create = function () {
        return __awaiter(this, void 0, void 0, function () {
            var channelsContent, channels, queue, _loop_1, this_1, _i, _a, channel;
            return __generator(this, function (_b) {
                switch (_b.label) {
                    case 0: return [4 /*yield*/, this.dataStorage.json('channels.json')];
                    case 1:
                        channelsContent = _b.sent();
                        channels = new core_1.Collection(channelsContent).map(function (data) { return new _1.ApiChannel(data); });
                        queue = new _1.Queue();
                        _loop_1 = function (channel) {
                            var configPath, config, found, days, currDate, dates;
                            return __generator(this, function (_c) {
                                switch (_c.label) {
                                    case 0:
                                        if (!channel.site || !channel.site_id || !channel.name)
                                            return [2 /*return*/, "continue"];
                                        if (this_1.options.lang && channel.lang !== this_1.options.lang)
                                            return [2 /*return*/, "continue"];
                                        configPath = path_1.default.resolve(constants_1.SITES_DIR, "".concat(channel.site, "/").concat(channel.site, ".config.js"));
                                        return [4 /*yield*/, this_1.configLoader.load(configPath)];
                                    case 1:
                                        config = _c.sent();
                                        if (channel.xmltv_id) {
                                            found = channels.first(function (_channel) { return _channel.id === channel.xmltv_id; });
                                            if (found) {
                                                channel.icon = found.logo;
                                                channel.name = found.name;
                                            }
                                        }
                                        else {
                                            channel.xmltv_id = channel.site_id;
                                        }
                                        days = this_1.options.days || config.days || 1;
                                        currDate = new core_1.DateTime(process.env.CURR_DATE || new Date().toISOString());
                                        dates = Array.from({ length: days }, function (_, day) { return currDate.add(day, 'd'); });
                                        dates.forEach(function (date) {
                                            var dateString = date.toJSON();
                                            var key = "".concat(channel.site, ":").concat(channel.lang, ":").concat(channel.xmltv_id, ":").concat(dateString);
                                            if (queue.missing(key)) {
                                                queue.add(key, {
                                                    channel: channel,
                                                    date: dateString,
                                                    config: config
                                                });
                                            }
                                        });
                                        return [2 /*return*/];
                                }
                            });
                        };
                        this_1 = this;
                        _i = 0, _a = this.parsedChannels.all();
                        _b.label = 2;
                    case 2:
                        if (!(_i < _a.length)) return [3 /*break*/, 5];
                        channel = _a[_i];
                        return [5 /*yield**/, _loop_1(channel)];
                    case 3:
                        _b.sent();
                        _b.label = 4;
                    case 4:
                        _i++;
                        return [3 /*break*/, 2];
                    case 5: return [2 /*return*/, queue];
                }
            });
        });
    };
    return QueueCreator;
}());
exports.QueueCreator = QueueCreator;
