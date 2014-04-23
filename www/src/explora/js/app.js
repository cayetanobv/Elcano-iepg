var app = app || {};
app.events = {};
_.extend(app.events , Backbone.Events);
app.defaults = {};

// variables. Array of countries with the countries to filter by
app.filters = [];

// Link to the base view
app.baseView = null;


Backbone.View.prototype.close = function(){
    this.remove();
    this.unbind();
  
    if (this.onClose){
        this.onClose();
    }
}


$(function(){

    $("body").on("click","a",function(e){
        console.log("here");
        var attr = $(this).attr("jslink"),
            href = $(this).attr("href");

        if (attr!= undefined && attr!="undefined"){
            e.preventDefault();
            if (href=="#back") {
                history.back();
            }
            app.router.navigate($(this).attr("href").substring(3),{trigger: true});
        }

        if (href=="#"){
            e.preventDefault();
        }
    });
    
    $(document).ajaxError(function(event, jqxhr, settings, exception) {
        if (jqxhr.status == 404) { app.router.navigate("notfound",{trigger: true});} 
        else { app.router.navigate("error",{trigger: true});}
    });
    app.ini();
});

app.resize = function(){
    var h = $(window).height()-this.$header.outerHeight(true) - this.$footer.outerHeight(true);
    this.$main.height(h);

    var toolDataMarginAndPadding = this.$tool_data.outerHeight(true) - this.$tool_data.height();

    this.$tool_data.height($(window).height() - this.$footer.outerHeight(true) - this.$tool_data.offset().top 
            - toolDataMarginAndPadding);

    //this.$tool_data.width( $(window).width() -  this.originLeft - 20).height();

    
}

app.ini = function(){
    this.lang = this.detectCurrentLanguage();
    this.router = new app.router();
    this.basePath = this.config.BASE_PATH + this.lang;
    this.$extraPanel = $("#extra_panel");
    this.$popup = $("#popup");
    this.$main = $("main");
    this.$header = $("header");
    this.$footer = $("footer");
    this.$tool_data = $("#tool_data");
    this.$tool = $("#tool");

    Backbone.history.start({pushState: true,root: this.basePath });

    app.context.restoreSavedContext();

    app.resize();

    $(window).resize(function(){
        app.resize();
    });
};

app.detectCurrentLanguage = function(){
    if (document.URL.indexOf("/es/") != -1 || document.URL.endsWith("/es")) {return "es";}
    else if (document.URL.indexOf("/en/") != -1 || document.URL.endsWith("/en")) {return "en";}
    return null;
};

app.getGlobalContext = function(){
    return this.context.data;
};

app.showViewInExtraPanel = function(view) {
    if (this.currentViewExtra){
      this.currentViewExtra.close();
    }
 
    this.currentViewExtra = view;
    //this.currentView.render();    
 
    this.$extraPanel.html(this.currentViewExtra.el);  
    this.$extraPanel.show()
    app.scrollTop();
}

app.showViewInPopup = function(view) {
    if (this.currentViewPopup){
      this.currentViewPopup.close();
    }
 
    this.currentViewPopup = view;
    //this.currentView.render();    
 
    this.$popup.html(this.currentViewPopup.el);

    app.scrollTop();
}

app.scrollTop = function(){
    var body = $("html, body");
    body.animate({scrollTop:0}, '500', 'swing', function() { 
       
    });
};

app.scrollToEl = function($el){
    $('html, body').animate({
        scrollTop: $el.offset().top
    }, 500);    
};

app.variableToString = function(variable){
    switch(variable){
        case 1:
            return "Índice Elcano de Presencia Global";
        case 2:
            return "Índice Elcano de Presencia Europea";

        // TODO complete this mapping 
        default:
            return "No definida"
    }
}





