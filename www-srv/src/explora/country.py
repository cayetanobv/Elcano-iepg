# coding=UTF8

"""

Explora country services.

"""
import common.datacache as datacache
import common.arrayops as arrayops
from explora import app
from flask import jsonify,request,send_file,make_response
from common.helpers import cacheWrapper, baseMapData
import common.arrayops
import json
from model import iepgdatamodel, basemap
from common.errorhandling import ElcanoApiRestError
from common.const import variables, years, blocks
import common.helpers
import common.const as const
from helpers import processFilter
import varengine.varengine as varengine
import numpy as numpy


@app.route('/countryfilter/<string:lang>', methods=['GET'])
def countryFilter(lang):
    if lang=="es":
        iso = datacache.isoToSpanish
    else:
        iso = datacache.isoToEnglish
    data = [{"id": k, "name": v, "short_name_"+lang+"_order": v} for (k,v) in iso.iteritems() 
            if k in datacache.countries]
    return(jsonify({"results": data}))


@app.route('/blocks/<string:lang>', methods=["GET"])
def blocksData(lang):
    """Retrieves currently available blocks data (based on filtered countries)."""
    if lang=="es":
        iso = datacache.isoToSpanish
    else:
        iso = datacache.isoToEnglish
    out = dict()
    for b in datacache.blocks:
        year = dict()
        for y in cacheWrapper(datacache.variables["iepg_energy"].getVariableYears):
            m = cacheWrapper(common.helpers.getBlockMembers, b, year=y)
            year[y] = m
        year["name"] = iso[b]
        out[b] = year

    return(jsonify(out))


@app.route('/countrysheet/<string:lang>/<string:family>/<string:countryCode>', methods=['GET'])
def countrySheet(lang, family, countryCode):
    """Retrieves all the data, for all years, and for a single country, to render the country sheet.
    Only retrieves context and IEPG variable families.
    Service call:

    /countrysheet/es/iepe/US?filter=US,DK,ES&entities=NL,XBEU,NZ

    entities is mandatory, although it has no effect in this tool.
    """
    m = iepgdatamodel.IepgDataModel()
    f = processFilter(request.args, "filter")
    familyVar = [v for (k,v) in datacache.variables.iteritems() if v.dataset.idDataset==family]
    contextVar = [v for (k,v) in datacache.variables.iteritems() if v.dataset.idDataset=="context"]
    # Participating countries
    countries = datacache.countries
    # Filter substraction
    if f:
        countries = arrayops.arraySubstraction(countries, f)

    try:
       out = dict()
       # Iterate through the years involved in the variable
       for year in familyVar[0].getVariableYears():
           yearData = dict()
           # Check if countryCode is a block. If it is, substract its members
           if countryCode in datacache.blocks:
               c = arrayops.arraySubstraction(countries, 
                                              cacheWrapper(common.helpers.getBlockMembers,
                                                           countryCode, year))
               c.append(countryCode)
           else:
               c = countries
   
           famVariables = dict()
           for var in familyVar:
               print "VAR: "+str(var)
               data = dict()
               data["code"] = countryCode
               v = cacheWrapper(common.helpers.getData, var, countryCode, year)

               ###HERE

               if not var.idVariable in ["military_global", "economic_global", "soft_global"]:
                   print("ii "+var.idVariable)
                   print "RT: "+family+"_relative_contribution_"+var.idVariable

                   vp = cacheWrapper(common.helpers.getData, 
                                     datacache.variables[family+"_relative_contribution_"+var.idVariable],
                                     countryCode, year)

                   print(vp)

               data["value"] = None if not v[0] or numpy.isnan(v[0]["value"]) else v[0]["value"]
               #data["percentage"] = None if not 
               data["variable"] = const.variableNames[family][var.idVariable]["name_"+lang]
               data["year"] = year
               data["globalranking"] = cacheWrapper(common.helpers.getRankingCode, datacache.countries, 
                                                    year, var,countryCode)
               data["relativeranking"] = cacheWrapper(common.helpers.getRankingCode, c, year,
                                                      var, countryCode)
               famVariables[var.idVariable] = data
   
           contextVariables = dict()
           for var in contextVar:
               data = dict()
               data["code"] = countryCode
               v = cacheWrapper(common.helpers.getData, var, countryCode, year)
               data["value"] = None if numpy.isnan(v[0]["value"]) else v[0]["value"]
               data["variable"] = const.variableNames["context"][var.idVariable]["name_"+lang]
               data["year"] = year
               data["globalranking"] = cacheWrapper(common.helpers.getRankingCode, datacache.countries, 
                                                    year, var,countryCode)
               data["relativeranking"] = cacheWrapper(common.helpers.getRankingCode, c, year,
                                                      var, countryCode)
               contextVariables[var.idVariable] = data
   
           yearData["iepg_variables"] = famVariables
           yearData["context_var"] = contextVariables
           comment = cacheWrapper(m.getIepgComment, lang, countryCode, year)
           yearData["comment"] = comment[0] if comment else None
           out[year] = yearData
       return(jsonify({"results": out}))
    except ElcanoApiRestError as e:
        return(jsonify(e.toDict()))


@app.route('/mapdata/<string:family>/<string:variable>/<int:year>', methods=['GET'])
def mapData(family, variable, year):
    """Retrieves map data. Service call:
    
    /mapdata/es/iepg/economic_presence/2013?filter=US,DK,ES&toolfilter=US,DK
    """
    filter = processFilter(request.args, "filter")
    toolFilter = processFilter(request.args, "toolfilter")
    if filter:
        c = arrayops.arraySubstraction(datacache.countries, filter)
    else:
        c = datacache.countries
    try:
        varData = cacheWrapper(common.helpers.getData, datacache.variables[family+"_"+variable], year=year,
                               countryList=c)
        varData = [c for c in varData if not numpy.isnan(c["value"])]
        return(jsonify({"results": varData}))
    except ElcanoApiRestError as e:
        return(jsonify(e.toDict()))    


@app.route('/mapgeojson', methods=['GET'])
def mapGeoJson():
    """Returns the map GeoJSON."""
    m = basemap.GeometryData()
    data = cacheWrapper(m.geometryData)
    out = dict()
    out["type"] = "FeatureCollection"
    
    features = []
    for d in data:
        f = dict()
        f["type"] = "Feature"
        f["geometry"] = json.loads(d["geojson"])
        fp = dict()
        fp["code"] = d["iso_3166_1_2_code"]
        fp["name_en"] = d["name_en"]
        fp["name_es"] = d["name_es"]
        f["properties"] = fp
        features.append(f)

    out["features"] = features

    return(jsonify(out))

###HERE > copy this output
@app.route('/globalindex/<string:family>/<string:countries>/<string:lang>', methods=['GET'])
def globalindex(family,countries,lang):
    from random import randint
    countriesArray = countries.split(",")
    dictResponse = { "results":[] }
    for c in countriesArray:
        dictResponse["results"].append({
            "country" : c,
            "years" : {
                "1990" : {
                    "value" :  randint(10,500)
                },
                "1995" : {
                    "value" :  randint(10,500)
                },
                "2000" : {
                    "value" :  randint(10,500)
                },
                "2005" : {
                    "value" :  randint(10,500)
                },
                "2010" : {
                    "value" :  randint(10,500)
                },
                "2013" : {
                    "value" :  randint(10,500)
                }
            }
        })

    return jsonify(dictResponse)
