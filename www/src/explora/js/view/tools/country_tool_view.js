app.view.tools.CountryPlugin = app.view.tools.Plugin.extend({
	_template : _.template( $('#country_tool_template').html() ),
    _templateChartLegend : _.template( $('#country_tool_chart_legend_template').html() ),
    type: "country",
  

    initialize: function(options) {
		this.slider = new app.view.tools.common.SliderSinglePoint();
		this.countries = new app.view.tools.common.Countries({
            "variable" : false
        });
    },

    _events: function(){
        return _.extend({},
            app.view.tools.Plugin.prototype._events.apply(this),
            {
               "mouseenter .infoover": function(e){
                    this.$(".content_infoover").fadeIn(300);
               },
               "mouseout .infoover": function(e){
                    this.$(".content_infoover").fadeOut(300);
               }
           }
        );
    },

    _setListeners: function(){
        app.view.tools.Plugin.prototype._setListeners.apply(this);

        //redefine the contextchange:countries to not re-render each time a country is added
        this.stopListening(app.events,"contextchange:countries");
        this.listenTo(app.events,"contextchange:countries",function(){
            //TOREMOVE
            console.log("contextchange:countries at app.view.tools.CountryPlugin");
            // The context has changed will be store by a call to contextToURL. 
            if (!app.context.data.countries.selection.length){
                // Let's force a re-render because we need to adapt the context.
                this.render(); // Implicit call to contextToURL
            }
            else{
                // No need of re-render, Let's refresh the list of countries
                this.countries.render();
                this.contextToURL();
            }
        });

        this.listenTo(app.events,"countryclick",function(id_country){
            //TOREMOVE
            console.log("countryclick at app.view.tools.CountryPlugin");

            var ctx = this.getGlobalContext();
            ctx.data.countries.selection = [id_country];

            // Render again the tool with the new context
            this._forceFetchDataTool = true;
            this._forceFetchDataMap = false;
            this.render(); // Implicit call to contextToURL
        });

        
    },

    /* Fetch data for the current country*/
	_fetchDataTool: function(){
        var ctxObj = this.getGlobalContext(),
            ctx = ctxObj.data;
        
        this.model = new app.model.tools.country({
            "id" : ctx.countries.selection[0],
            "family" : ctx.family
        });

        // Fetch model from de server
        var self = this;
        this.model.fetch({
            success: function() {
               self._renderToolAsync();
            }
        });
	},

    _fetchDataMap: function(){

        var ctxObj = this.getGlobalContext(),
            ctx = ctxObj.data;

        // Fetch the collection from the server
        this.mapCollection = new app.collection.CountryToolMap([],{
            "family" :  ctx.family,
            "variable" : ctx.family, // this is a trick, the map of this tool always show the family variable
            "date" : ctx.slider[0].date.getFullYear()
        });
        
        this.listenTo(this.mapCollection,"reset",this._renderMapAsync);

        this.mapCollection.fetch({"reset":true});

    },

    _renderToolAsync: function(){
        var year =  this.getGlobalContext().data.slider[0].date.getFullYear();

        this.$el.html(this._template({
            ctx: this.getGlobalContext().data,
            model: this.model.toJSON()[year],
        }));

        this.$chart_legend = this.$(".chart_legend");

        this.$chart = this.$(".chart");

        this._drawD3Chart(year);

        this._renderChartLegend(year,"iepg");

        this._forceFetchDataTool = false;
    },

    _renderMapAsync: function(){
        this._forceFetchDataTool = false;
        this.mapLayer = app.map.drawChoropleth(this.mapCollection.toJSON());
    },

    /* Render the tool */
    renderTool: function(){
        //TOREMOVE
        console.log("Render app.view.tools.CountryPlugin");

        var ctxObj = this.getGlobalContext(),
            ctx = ctxObj.data;

        if (!ctx.countries.selection.length){
            // it happens when remove the latest element from the filter
            this.$el.html(this._template({
                ctx: this.getGlobalContext().data,
                model: null,
            }));
        }
        else{
            // Get the data from server if _forceFetchDataTool is set to true. If _forceFetchDataTool is set to false data is not requested to server
            if (this._forceFetchDataTool){
                this._fetchDataTool();
            }
            else{
                this._renderToolAsync();
            }
        }

        this.renderMap();
    },

    renderMap: function(){
        if (this._forceFetchDataMap){

            this._fetchDataMap();
        }
        else{
            this._renderMapAsync();
        }
    },

    clearMap: function(){
        app.map.removeChoropleth();
    },

    onClose: function(){
        // Remove events on close
        this.stopListening();
    },

    /* 
        This method adapt the global context
    */
    adaptGlobalContext: function(){

        var ctxObj = this.getGlobalContext(),
            ctx = ctxObj.data,
            latestCtxObj = this.getLatestContext(),
            latestCtx = latestCtxObj.data;

        /*
        * This tool only has a country selected. The options are:
        *   1) The selection is empty
        *       1.1) If The latestContext has a selection and the country selected is on the list of countries, this will be taken.
        *       1.2) If The latestContext doesn't have a selection, the first on the list will be the selected.
        *   2) The selection has elements. All except the first one will be removed.
        */
        
        if (!ctx.countries.selection.length){
            // The selection is empty
           
            if (latestCtx.selection>0 && ctx.countries.list.indexOf(latestCtx.selection[0])!=-1){
                // If The latestContext has a selection and the country selected is on the list of countries
                ctx.countries.selection = [latestCtx.selection[0]];
            }
            else{
                // the first on the list will be the selected
                ctx.countries.selection = ctx.countries.list.length ? [ctx.countries.list[0]] : [];
            }
        }
        else{
            // All except the first one will be removed.
            ctx.countries.selection = [ctx.countries.selection[0]];
        }


        // This tool works with a single point slider. 
        var firstPoint = ctxObj.getFirstSliderElement("Point");

        if (firstPoint){
            // Get the first point and remove the others from the context.
            ctx.slider = [firstPoint];
        }
        else{
            // search the firstPoint on the latest context
            var firstPoint = latestCtxObj.getFirstSliderElement("Point");
            if (firstPoint){
                // Get the first point from the latest context and remove the others
                ctx.slider = [firstPoint];
            }
            else{
                // set the last year
                ctx.slider = [{
                    "type" : "Point",
                    "date" : app.config.SLIDER[app.config.SLIDER.length-1]
                }];
            }
        }

        if (!ctx.family){
            if (latestCtx.family){
                ctx.family = latestCtx.family;
            }
            else{
                ctx.family = "iepg";
            }
        }

        // Save context
        ctxObj.saveContext();

        // update the latest context
        this.copyGlobalContextToLatestContext();
    },

    contextToURL: function(){
        // This method transforms the current context of the tool in a valid URL.
        //country/:id_country/:id_variable/:year
        var ctxObj = this.getGlobalContext(),
            ctx = ctxObj.data,
            family = ctx.family,
            countries = ctx.countries.list.join(","),
            country = ctx.countries.selection[0],
            variable = ctx.variables[0],
            year = ctx.slider[0].date.getFullYear()
            filters = app.getFilters().length ? "/" + app.getFilters().join(",") : "";
            url = "country/" + family + "/" + countries + "/" + country + "/" + year + filters;

         app.router.navigate(url, {trigger: false});
    },

    URLToContext: function(url){

        var ctxObj = app.context,
            ctx = ctxObj.data;
            
        ctx.family = url.family;
        ctx.countries.list = url.countries.split(",");
        ctx.countries.selection = [url.country_sel];
        ctx.countries.slider = [{
            "type": "Point",
            "date" : new Date(url.year)
        }];

        // Do we have filters?
        if (url.filters){
            app.setFilters(url.filters.split(","));
        }

        ctx.countries.slider = [{
            "type": "Point",
            "date" : new Date(url.year)
        }];

        // let's store the context.
        ctxObj.saveContext();

        this.copyGlobalContextToLatestContext();

    },

    _drawD3Chart: function(year){
        var width = this.$chart.width(),
            height = this.$chart.height(),
            radius = Math.min(width, height) / 2;

        var x = d3.scale.linear()
            .range([0, 2 * Math.PI]);

        var y = d3.scale.sqrt()
            .range([0, radius]);

        var color = d3.scale.category20c();

        var svg = d3.select(".chart").append("svg")
            .attr("width", width)
            .attr("height", height)
          .append("g")
            .attr("transform", "translate(" + width / 2 + "," + (height / 2 ) + ")")
            .attr("class", "variable");

        var partition = d3.layout.partition()
            .value(function(d) { return d.size; });

        var arc = d3.svg.arc()
            .startAngle(function(d) { return Math.max(0, Math.min(2 * Math.PI, x(d.x))); })
            .endAngle(function(d) { return Math.max(0, Math.min(2 * Math.PI, x(d.x + d.dx))); })
            .innerRadius(function(d) { return Math.max(0, y(d.y)); })
            .outerRadius(function(d) { return Math.max(0, y(d.y + d.dy)); });

        d3.select(self.frameElement).style("height", height + "px");

        // Interpolate the scales!
        function arcTween(d) {
          var xd = d3.interpolate(x.domain(), [d.x, d.x + d.dx]),
              yd = d3.interpolate(y.domain(), [d.y, 1]),
              yr = d3.interpolate(y.range(), [d.y ? 20 : 0, radius]);
          return function(d, i) {
            return i
                ? function(t) { return arc(d); }
                : function(t) { x.domain(xd(t)); y.domain(yd(t)).range(yr(t)); return arc(d); };
          };
        }

        var div = d3.select("body").append("div")   
        .attr("class", "tooltip")               
        .style("opacity", 0);

        var obj = this;

        var root = this._buildModelTree(year),
            path = svg.selectAll("path")
              .data(partition.nodes(root))
            .enter().append("path")
              .attr("d", arc)
              .style("fill", function(d) { return d.color; })
            .on("click", click)
            .on("mouseover", function(d) {     
                div.transition()        
                    .duration(200)      
                    .style("opacity", 1);      
                div.html(obj._htmlToolTip(d.name))  
                    .style("left", (d3.event.pageX) + "px")     
                    .style("top", (d3.event.pageY - 28) + "px");    
                })                  
            .on("mouseout", function(d) {       
                div.transition()        
                    .duration(500)      
                    .style("opacity", 0);   
            });
        

            function click(d) {
                if (d.name == "iepg" || d.name == "economic_presence" ||
                    d.name == "soft_presence" || d.name =="military_presence")
                {
                    path.transition()
                        .duration(750)
                        .attrTween("d", arcTween(d));
                    obj._renderChartLegend(year,d.name);
                }
          }
    },

    _htmlToolTip: function(variable){
        var year =  this.getGlobalContext().data.slider[0].date.getFullYear(),
            variable = this.model.get(year).iepg_variables[variable];

            html = "<div>" 
                    +   "<span>" + variable.ranking + "º " +app.countryToString(variable.code) + "</span>"
                    +   "<span>" + year + "</span>"
                    +   "<div class='clear'></div>"
                    + "</div>"
                    + "<div>" 
                    +   "<span>" + variable.variable + "</span>"
                    +   "<span>" + sprintf("%0.2f",variable.value) + "</span>"
                    +   "<div class='clear'></div>"
                    +"</div>"

        return html;

    },

    _buildModelTree: function(year){

        var variables = this.model.get(year).iepg_variables;
        return {
            "name" : "iepg",
            "color" : "#fdc300",
            "size" : variables.iepg.value,
            "children" : [{
                "name" : "economic_presence",
                "color" : "#2b85d0",
                "size" : variables.economic_presence.value,
                "children": [{
                    "name" : "energy",
                    "size" : variables.energy.value,
                    "color" : "#4191d5"
                },
                {
                    "name" : "primary_goods",
                    "size" : variables.primary_goods.value,
                    "color" : "#559dd9"
                },
                {
                    "name" : "manufactures",
                    "size" : variables.manufactures.value,
                    "color" : "#6baade"
                },
                 {
                    "name" : "services",
                    "size" : variables.services.value,
                    "color" : "#80b6e3"
                },
                {
                    "name" : "investments",
                    "size" : variables.investments.value,
                    "color" : "#95c2e7"
                }
                ]
            },{
                "name" : "military_presence",
                "color" : "#669900",
                "size" : variables.military_presence.value,
                "children": [{
                        "name" : "troops",
                        "size" : variables.troops.value,
                        "color" : "#76a318"
                    },{
                        "name" : "military_equipment",
                        "size" : variables.military_equipment.value,
                        "color" : "#85ad33"

                    }]
            },{
                "name" : "soft_presence",
                "color" : "#ff9000",
                "size" : variables.soft_presence.value,
                "children": [{
                        "name" : "migrations",
                        "size" : variables.migrations.value,
                        "color" : "#ff960d",
                    },{
                        "name" : "tourism",
                        "size" : variables.tourism.value,
                        "color" : "#ff9b1a"
                    },{
                        "name" : "sports",
                        "size" : variables.sports.value,
                        "color" : "#ffa126"
                    },{
                        "name" : "culture",
                        "size" : variables.culture.value,
                        "color": "#ffa633"
                    },{
                        "name" : "information",
                        "size" : variables.information.value,
                        "color" : "#ffac40"
                    },{
                        "name" : "technology",
                        "size" : variables.technology.value,
                        "color" : "#ffb24d"
                     },{
                        "name" : "science",
                        "size" : variables.science.value,
                        "color" : "#ffb759"
                    },{
                        "name" : "education",
                        "size" : variables.education.value,
                        "color" : "#ffbc66"
                    },{
                        "name" : "cooperation",
                        "size" : variables.cooperation.value,
                        "color" : "#ffc273"
                    }]
            }

            ]
        }
    },

    _extractNodeFromTree: function(year,name){
        var nodes = this. _buildModelTree(year);
        if (name == "iepg"){
            return nodes;
        }
        else{
            nodes = nodes.children;
        }
       
        // find the node in the childrens
        for(var i=0;i<nodes.length;i++){
            if (nodes[i].name == name){
                return nodes[i];
            }
        }

        return null;
    },

    _renderChartLegend: function(year,name){

        this.$chart_legend.html(this._templateChartLegend({
            data: this._extractNodeFromTree(year,name)
        }));

    }
    
});