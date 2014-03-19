var app = app || {};

app.collection.Docs = Backbone.Collection.extend({
    model: Backbone.Model,
    search: null,
    offset: 0,
    initialize: function(models, options) {

    },
    url : function() {
        var search = this.search ? "&search=" + this.search : "";
        return app.config.API_URL + "/documentcatalog" + "?lang=" + app.lang + "&offset=" + this.offset + search;
    },
    parse: function(response){
        this.listSize = response.listSize;
        return response.results;
    }
    
});
