var app = app || {};

app.collection.Slider = Backbone.Collection.extend({
    model: Backbone.Model,
    
    initialize: function(models, options) {
        
    },
    url : function() {
       
        return app.config.API_URL + "/home/slider/" + app.lang ;
    },

    parse: function(response){
        return response.results;
    }

    
});
