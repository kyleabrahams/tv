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
var core_1 = require("@freearhey/core");
var commander_1 = require("commander");
var cron_1 = require("cron");
var core_2 = require("../../core");
var path_1 = require("path");
var constants_1 = require("../../constants");
commander_1.program
    .option('-s, --site <name>', 'Name of the site to parse')
    .option('-c, --channels <path>', 'Path to *.channels.xml file (required if the "--site" attribute is not specified)')
    .option('-o, --output <path>', 'Path to output file', 'guide.xml')
    .option('-l, --lang <code>', 'Filter channels by language (ISO 639-2 code)')
    .option('-t, --timeout <milliseconds>', 'Override the default timeout for each request')
    .option('-d, --delay <milliseconds>', 'Override the default delay between request')
    .option('--days <days>', 'Override the number of days for which the program will be loaded (defaults to the value from the site config)', function (value) { return parseInt(value); })
    .option('--maxConnections <number>', 'Limit on the number of concurrent requests', function (value) { return parseInt(value); }, 1)
    .option('--cron <expression>', 'Schedule a script run (example: "0 0 * * *")')
    .option('--gzip', 'Create a compressed version of the guide as well', false)
    .parse(process.argv);
var options = commander_1.program.opts();
function main() {
    return __awaiter(this, void 0, void 0, function () {
        var logger, storage, parser, files, pattern, parsedChannels, _i, files_1, filepath, _a, _b, runIndex, cronJob;
        var _this = this;
        return __generator(this, function (_c) {
            switch (_c.label) {
                case 0:
                    if (!options.site && !options.channels)
                        throw new Error('One of the arguments must be presented: `--site` or `--channels`');
                    logger = new core_1.Logger();
                    logger.start('starting...');
                    logger.info('config:');
                    logger.tree(options);
                    logger.info('loading channels...');
                    storage = new core_1.Storage();
                    parser = new core_2.ChannelsParser({ storage: storage });
                    files = [];
                    if (!options.site) return [3 /*break*/, 2];
                    pattern = path_1.default.join(constants_1.SITES_DIR, options.site, '*.channels.xml');
                    pattern = pattern.replace(/\\/g, '/');
                    return [4 /*yield*/, storage.list(pattern)];
                case 1:
                    files = _c.sent();
                    return [3 /*break*/, 4];
                case 2:
                    if (!options.channels) return [3 /*break*/, 4];
                    return [4 /*yield*/, storage.list(options.channels)];
                case 3:
                    files = _c.sent();
                    _c.label = 4;
                case 4:
                    parsedChannels = new core_1.Collection();
                    _i = 0, files_1 = files;
                    _c.label = 5;
                case 5:
                    if (!(_i < files_1.length)) return [3 /*break*/, 8];
                    filepath = files_1[_i];
                    _b = (_a = parsedChannels).concat;
                    return [4 /*yield*/, parser.parse(filepath)];
                case 6:
                    parsedChannels = _b.apply(_a, [_c.sent()]);
                    _c.label = 7;
                case 7:
                    _i++;
                    return [3 /*break*/, 5];
                case 8:
                    if (options.lang) {
                        parsedChannels = parsedChannels.filter(function (channel) { return channel.lang === options.lang; });
                    }
                    logger.info("  found ".concat(parsedChannels.count(), " channel(s)"));
                    runIndex = 1;
                    if (options.cron) {
                        cronJob = new cron_1.CronJob(options.cron, function () { return __awaiter(_this, void 0, void 0, function () {
                            return __generator(this, function (_a) {
                                switch (_a.label) {
                                    case 0:
                                        logger.info("run #".concat(runIndex, ":"));
                                        return [4 /*yield*/, runJob({ logger: logger, parsedChannels: parsedChannels })];
                                    case 1:
                                        _a.sent();
                                        runIndex++;
                                        return [2 /*return*/];
                                }
                            });
                        }); });
                        cronJob.start();
                    }
                    else {
                        logger.info("run #".concat(runIndex, ":"));
                        runJob({ logger: logger, parsedChannels: parsedChannels });
                    }
                    return [2 /*return*/];
            }
        });
    });
}
main();
function runJob(_a) {
    return __awaiter(this, arguments, void 0, function (_b) {
        var timer, queueCreator, queue, job;
        var logger = _b.logger, parsedChannels = _b.parsedChannels;
        return __generator(this, function (_c) {
            switch (_c.label) {
                case 0:
                    timer = new core_1.Timer();
                    timer.start();
                    queueCreator = new core_2.QueueCreator({
                        parsedChannels: parsedChannels,
                        logger: logger,
                        options: options
                    });
                    return [4 /*yield*/, queueCreator.create()];
                case 1:
                    queue = _c.sent();
                    job = new core_2.Job({
                        queue: queue,
                        logger: logger,
                        options: options
                    });
                    return [4 /*yield*/, job.run()];
                case 2:
                    _c.sent();
                    logger.success("  done in ".concat(timer.format('HH[h] mm[m] ss[s]')));
                    return [2 /*return*/];
            }
        });
    });
}
