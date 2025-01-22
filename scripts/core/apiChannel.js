"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ApiChannel = void 0;
var core_1 = require("@freearhey/core");
var ApiChannel = /** @class */ (function () {
    function ApiChannel(_a) {
        var id = _a.id, name = _a.name, alt_names = _a.alt_names, network = _a.network, owners = _a.owners, country = _a.country, subdivision = _a.subdivision, city = _a.city, broadcast_area = _a.broadcast_area, languages = _a.languages, categories = _a.categories, is_nsfw = _a.is_nsfw, launched = _a.launched, closed = _a.closed, replaced_by = _a.replaced_by, website = _a.website, logo = _a.logo;
        this.id = id;
        this.name = name;
        this.altNames = new core_1.Collection(alt_names);
        this.network = network;
        this.owners = new core_1.Collection(owners);
        this.country = country;
        this.subdivision = subdivision;
        this.city = city;
        this.broadcastArea = new core_1.Collection(broadcast_area);
        this.languages = new core_1.Collection(languages);
        this.categories = new core_1.Collection(categories);
        this.isNSFW = is_nsfw;
        this.launched = launched;
        this.closed = closed;
        this.replacedBy = replaced_by;
        this.website = website;
        this.logo = logo;
    }
    return ApiChannel;
}());
exports.ApiChannel = ApiChannel;
