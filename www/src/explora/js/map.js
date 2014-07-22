app.view.map = function(options){
    this.baseLayer = null;

    //this._choroplethColors = ["#800026","#BD0026","#E31A1C","#FC4E2A","#FD8D3C"];
    this._choroplethColors = ["#ffd88b","#f9be84","#fa976a","#ee6756","#de3338"];

    this.CHOROPLETH_INTERVALS = 5;

    this._choroplethOVerlay = null;

    this.container = options.container;
    this.zoom = options.zoom ? options.zoom : 2;
    this.center = options.center ? options.center  : L.latLng(0,0);
    this.$tooltip = options.tooltip ? options.tooltip : $("#map_tooltip");
    this.$maplabel = options.maplabel ? options.maplabel : $("#map_label");
    this.$maplegend = options.maplegend ? options.maplegend : $("#map_legend");

    this.initialize = function(options){

        var southWest = L.latLng(-85, -190),
        northEast = L.latLng(85,190),
        bounds = L.latLngBounds(southWest, northEast);

        this._map = L.map(this.container,{
            "attributionControl" : false,
            "zoomControl" : false,
            // It doesn't work in ranking tool
            "maxBounds" : bounds,
            "minZoom": 2
        }).setView( this.center, this.zoom);

        this.loadBaseMap();
    
        return this;
    };

    this.loadBaseMap = function(){
        this._baseLayer = L.geoJson(countriesGeoJSON, {
            style: {
                fillColor: "#fff",
                weight: 1,
                opacity: 1,
                color: '#a2a2ac',
                // dashArray: '3',
                fillOpacity: 1
            }
        });
        this._baseLayer.addTo(this._map);  
    };

    /* Resize the map */ 
    this.resize = function(){
        this._map.invalidateSize(true);
        return this;
    };

    this.getMap = function(){
        return this._map;
    };

    /* This method created a choropleth Map with the data supplied in the parameter */ 
    this.drawChoropleth = function(data,time,variable,family,units){


        if (!units) units = ""

        var n_intervals = data.length < this.CHOROPLETH_INTERVALS ? data.length :  this.CHOROPLETH_INTERVALS ;
        // Just for security
        if (!data || !data.length) return;


        this._choroplethColors = app.view.tools.utils.getChoroplethColors(family,variable)

        // Remove previous choropleth, needed for redraws
        this.removeChoropleth();

        var bigJSON = [],
            values = _.pluck(data,"value"),
            max = _.max(values),
            min = _.min(values),
            rangeData = max - min;

        // We build the GeoJSON, for the choropleth
        for (var i=0;i<data.length;i++){
            if (!data[i].code){
                continue;
            }

            if(data[i].code.length>2){
                //It's a block, let's find all countries inside this block
                for(var j=0;j<app.blocks[data[i].code][time].length;j++){
                    var country = app.findCountry(app.blocks[data[i].code][time][j]);
                    if (!country){
                        continue;
                    }
                    country.properties.code = data[i].code;
                    country.properties.name_es = app.blocks[data[i].code]["name_es"];
                    country.properties.name_en = app.blocks[data[i].code]["name_en"];
                    country.properties.time = time;
                    country.properties.value = data[i].value;
                    country.properties.variable = variable;
                    country.properties.family = family;

                    bigJSON.push(country);
                   
                }
            }
            else{
                var country = app.findCountry(data[i].code);
                if (!country){
                    continue;
                }
                country.properties.time = time;
                country.properties.value = data[i].value;
                country.properties.variable = variable;
                country.properties.family = family;
                bigJSON.push(country);
            }
           

            
        }

        var _this = this;

        function getColor(d){

            if (d == max){
                return _this._choroplethColors[ n_intervals-1];
            }
            else if (d==min){
                return _this._choroplethColors[0];
            }
            else{
                var index = parseInt(  ((d-min) *  n_intervals) /
                                    rangeData );
                return _this._choroplethColors[index];
            }
        }

        function style(feature) {
            return {
                fillColor: getColor(feature.properties.value),
                weight: 1,
                opacity: 1,
                color: 'white',
                fillOpacity: 1
            };
        }

        function highlightFeature(e) {
            var layer = e.target;

            layer.setStyle({
                weight: 1,
                color: '#28282b',
                // dashArray: '',
                fillOpacity: 1
            });

            if (!L.Browser.ie && !L.Browser.opera) {
                layer.bringToFront();
            }
            
            _this.$tooltip.css("left",e.containerPoint.x).css("top",e.containerPoint.y);

            var v = layer.feature.properties;
            
            var html = "<div>" 
                    +   "<span>" +app.countryToString(v.code) + "</span>"
                    +   "<span>" + v.time + "</span>"
                    +   "<div class='clear'></div>"
                    + "</div>"
                    + "<div>" 
                    +   "<span>" + app.variableToString(v.variable,v.family) + "</span>"
                    +   "<span>" + app.formatNumber(v.value) + units + "</span>"
                    +   "<div class='clear'></div>"
                    +"</div>";

            _this.$tooltip.html(html);
            
            _this.$tooltip.show();
        }

        function resetHighlight(e) {
            l.resetStyle(e.target);
            _this.$tooltip.hide();
        }

        function zoomToFeature(e) {
            this._map.fitBounds(e.target.getBounds());
        }

        function onEachFeature(feature, layer) {
            layer.on({
                mouseover: highlightFeature,
                mouseout: resetHighlight,
                click: zoomToFeature
            });
        }

        var l = L.geoJson(bigJSON, {
            style: style,
            onEachFeature: onEachFeature
        });

        l.addTo(this._map);

        // Let's add a legend for the map. 

       
        var grades = [],
            labels = [],
            inc = parseInt(max/n_intervals);

        for (var i=0;i<n_intervals;i++){
            grades.push(parseInt(i*inc + min));
        }

        // loop through our density intervals and generate a label with a colored square for each interval
        var html = "<ul>";
        
        for (var i=0;i<n_intervals;i++){
            html +=
                "<li> " +
                    "<span style='background: "+ getColor(grades[i] +1) + "'></span>" +
                    "<span> " +grades[i] + (grades[i + 1] ? '&ndash;' + grades[i + 1] + '' : '+') + "</span>" +
                "</li>";
        }
        html += "</ul>";

        this.$maplegend.html(html);

        this.$maplabel.find(".variable").html(app.variableToString(variable,family));
        this.$maplabel.find(".time").html(time);

        this.$maplabel.show();

        this._choroplethOVerlay = {
            "geoJson" : l,
        };

        this.$maplegend.show();

        return l;
    };

    this.removeChoropleth = function(){
       
        if (this._choroplethOVerlay){   
            this._map.removeLayer(this._choroplethOVerlay["geoJson"]);
            this.$tooltip.hide();
            this.$maplegend.hide();
            this.$maplabel.hide();
            
            this._choroplethOVerlay = null;
        }

        return this;
    }

    this.zoomIn = function(){
        this._map.setZoom(this._map.getZoom()+1);
    }

    this.zoomOut = function(){
        this._map.setZoom(this._map.getZoom()-1);
    }

      

}