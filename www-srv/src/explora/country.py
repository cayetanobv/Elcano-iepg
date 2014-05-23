# coding=UTF8

"""

Explora country services.

"""
from explora import app
from flask import jsonify,request,send_file,make_response
from common.helpers import cacheWrapper, baseMapData, arrayIntersection
import json
from model import iepgdatamodel, basemap
from common.errorhandling import ElcanoApiRestError
from common.const import variables, years, blocks
import common.helpers
from helpers import processFilter



# TEST BEGINS 

from common.helpers import blocksSumCalculateData

# @app.route('/test/<string:blockCode>/<int:year>/<string:family>/<string:variable>', methods=["GET"])
# def test(blockCode, year, family, variable):
#     print(blocksGetData(blockCode))

#     print(blocksSumCalculateData(blockCode, year, family, variable))

#     return(jsonify({"results": "caca"}))


# TEST ENDS




@app.route('/countryfilter/<string:lang>', methods=['GET'])
def countryFilter(lang):
    m = iepgdatamodel.IepgDataModel()
    try:
        return(jsonify({"results": cacheWrapper(m.countryFilter, lang)}))
    except ElcanoApiRestError as e:
        return(jsonify(e.toDict()))


@app.route('/blocks/<string:lang>/<int:year>', methods=["GET"])
def blocksData(lang, year):
    """Retrieves currently available blocks data (based on filtered countries).
    Params:
    
    filter: country filter
    """
    if "filter" in request.args:
        countryFilter = request.args["filter"]
        if countryFilter=="":
            countryFilter = None
        else:
            countryFilter = countryFilter.split(",")
    else:
        countryFilter = None

    m = iepgdatamodel.IepgDataModel()
    out = dict()
    for blockCode,blockData in blocks.items():
        block = dict()
        block["name"] = blockData["name_"+lang]
        blockYears = dict()
        for year,membersData in blockData["members"].items():
            if countryFilter:
                if arrayIntersection(membersData, countryFilter)<>[]:
                    continue
            countries = dict()
            for countryCode in membersData["countries"]:
                countryName = cacheWrapper(m.getCountryNameByIso2, countryCode, lang)[0]
                countries[countryCode] = countryName
            blockYears[year] = countries
        block["members"] = blockYears
        if block["members"]<>{}:
            out[blockCode] = block
    return(jsonify(out))


@app.route('/countrysheet/<string:lang>/<string:family>/<string:countryCode>', methods=['GET'])
def countrySheet(lang, family, countryCode):
    """Retrieves all the data, for all years, and for a single country, to render the country sheet.
    Only retrieves context and IEPG variable families.
    Service call:

    /countrysheet/es/iepe/US?filter=US,DK,ES&entities=NL,XBEU,NZ

    entities is mandatory
    """
    m = iepgdatamodel.IepgDataModel()
    f = processFilter(request.args, "filter")
    e = processFilter(request.args, "entities")
    blocksEntities,countriesEntities = common.helpers.getBlocksFromCountryList(e) if e else (None, None)

    print(blocksEntities, countriesEntities)
    countriesEntities = common.helpers.arraySubstraction(countriesEntities, f)

    print(f)
    print(blocksEntities, countriesEntities)

    

    print (common.helpers.getVariableYears(family))

    ###HERE


    # try:
    #     data = dict()
    #     for year in years:
    #         y = dict()
    #         iepg_var = dict()
    #         context_var = dict()
    #         for var,item in variables.items():
    #             if item["family"]=="iepg":
    #                 rankData = cacheWrapper(m.ranking, lang, countryCode, 
    #                                         "iepg", item["key"], year, filter=filter, toolFilter=toolFilter)
    #                 iepg_var[item["key"]] = rankData[0]
    #             if item["family"]=="context":
    #                 rankData = cacheWrapper(m.ranking, lang, countryCode, 
    #                                         "context", item["key"], year, filter=filter, toolFilter=toolFilter)
    #                 context_var[item["key"]] = rankData[0]

    #         y["iepg_variables"] = iepg_var
    #         y["context_var"] = context_var
    #         y["comment"] = cacheWrapper(m.getIepgComment, lang, countryCode, year)[0]
    #         data[year]=y
    #     return(jsonify({"results": data}))
    # except ElcanoApiRestError as e:
    #     return(jsonify(e.toDict()))

    return(jsonify({"E": 1}))

@app.route('/mapdata/<string:family>/<string:variable>/<int:year>', methods=['GET'])
def mapData(family, variable, year):
    """Retrieves map data. Service call:
    
    /mapdata/es/iepg/economic_presence/2013?filter=US,DK,ES&toolfilter=US,DK
    """
    filter = processFilter(request.args, "filter")
    toolFilter = processFilter(request.args, "toolfilter")
    m = iepgdatamodel.IepgDataModel()

    try:
        varData = cacheWrapper(m.variableData, family, variable, year, filter=filter, toolFilter=toolFilter)
    except ElcanoApiRestError as e:
        return(jsonify(e.toDict()))    

    return(jsonify({"results": varData}))


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
