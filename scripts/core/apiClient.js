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
exports.ApiClient = void 0;
var core_1 = require("@freearhey/core");
var axios_1 = require("axios");
var cli_progress_1 = require("cli-progress");
var numeral_1 = require("numeral");
var ApiClient = /** @class */ (function () {
    function ApiClient(_a) {
        var logger = _a.logger;
        this.logger = logger;
        this.client = axios_1.default.create({
            responseType: 'stream'
        });
        this.storage = new core_1.Storage();
        this.progressBar = new cli_progress_1.default.MultiBar({
            stopOnComplete: true,
            hideCursor: true,
            forceRedraw: true,
            barsize: 36,
            format: function (options, params, payload) {
                var filename = payload.filename.padEnd(18, ' ');
                var barsize = options.barsize || 40;
                var percent = (params.progress * 100).toFixed(2);
                var speed = payload.speed ? (0, numeral_1.default)(payload.speed).format('0.0 b') + '/s' : 'N/A';
                var total = (0, numeral_1.default)(params.total).format('0.0 b');
                var completeSize = Math.round(params.progress * barsize);
                var incompleteSize = barsize - completeSize;
                var bar = options.barCompleteString && options.barIncompleteString
                    ? options.barCompleteString.substr(0, completeSize) +
                        options.barGlue +
                        options.barIncompleteString.substr(0, incompleteSize)
                    : '-'.repeat(barsize);
                return "".concat(filename, " [").concat(bar, "] ").concat(percent, "% | ETA: ").concat(params.eta, "s | ").concat(total, " | ").concat(speed);
            }
        });
    }
    ApiClient.prototype.download = function (filename) {
        return __awaiter(this, void 0, void 0, function () {
            var stream, bar;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0: return [4 /*yield*/, this.storage.createStream("/temp/data/".concat(filename))];
                    case 1:
                        stream = _a.sent();
                        bar = this.progressBar.create(0, 0, { filename: filename });
                        this.client
                            .get("https://iptv-org.github.io/api/".concat(filename), {
                            onDownloadProgress: function (_a) {
                                var total = _a.total, loaded = _a.loaded, rate = _a.rate;
                                if (total)
                                    bar.setTotal(total);
                                bar.update(loaded, { speed: rate });
                            }
                        })
                            .then(function (response) {
                            response.data.pipe(stream);
                        });
                        return [2 /*return*/];
                }
            });
        });
    };
    return ApiClient;
}());
exports.ApiClient = ApiClient;
