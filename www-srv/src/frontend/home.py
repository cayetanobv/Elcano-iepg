# coding=UTF8

"""
Frontend home services.
"""
from frontend import app
from flask import jsonify,request
from flask.json import dump
from model.homemodel import HomeModel
from model.iepgdatamodel import IepgDataModel
from model.highlightmodel import HighlightModel
from model.labelmodel import LabelModel
import helpers
import common.helpers
from common import config as config
from common import const as cons
from model.helpers import ElcanoError, ElcanoErrorBadNewsSection, ElcanoErrorBadLanguage
import locale
import common.datacache as datacache
from collections import OrderedDict


@app.route('/home/email', methods=['POST'])
def postEmail():
    """Inserts an email into the list. request.args: 
      email: mandatory
    """
    m = HomeModel()
    return(jsonify({"email": m.newEmail(request.args["email"])}))


@app.route('/home/slider/<string:lang>', methods=['GET'])
def getSliderFrontend(lang):
    """Gets the slider's data."""
    m = HighlightModel()
    
    try:
        out = m.getSliderFrontend(lang)
        return(jsonify({"results": out}))
    except ElcanoErrorBadLanguage as e:
        return(jsonify(e.dict()))


@app.route('/home/countries', methods=['GET'])
def countries():
    """Returns list of geopolitical blocks and its countries for a
    language and a year. Parameters are:

      lang=en/es: required
      year: required

    Returns a JSON:

    {
    results: [
    {
      "block":
        {
          "name": "América",
          "ncountries": "2",
          "countries": [
            {"name": "USA"},
            {"name": "Canadá"}
          ]
        }
    },
    ]
    }
      
    """
    lang = request.args["lang"]
    year = request.args["year"]
    if lang=="es":
        trans = datacache.isoToSpanish
    if lang=="en":
        trans = datacache.isoToEnglish

    blocks = []
    for block in datacache.blocksNoEu:
        print block
        dBlock = dict()
        dBlock["code"] = block
        dBlock["name"] = trans[block]
        dBlock["countries"] = []
        countries = common.helpers.getBlockMembers(block, year)
        dBlock["countries"] = sorted([{"code": i, "name": trans[i]} for i in countries], 
                                     key=lambda t: t["name"])
        dBlock["ncountries"] = len(dBlock["countries"])
        blocks.append(dBlock)

    return(jsonify({"results": sorted(blocks, key=lambda t: t["name"])}))


@app.route('/home/years', methods=['GET'])
def years():
    """Returns the list of years in IEPG data. JSON is:

    {
      "results": [
        {
          "year": "2012"
        }
      ]
    }

    """
    m = IepgDataModel()
    a = m.years()

    return(jsonify({"results": a}))
        

@app.route('/home/newstuff', methods=['GET'])
def newStuff():
    """Returns new stuff for the new stuff control. Accepts request.args:

      lang=en/es: mandatory 
      section= 1=Blog/2=Media/3=Events/4=Documents/5=Twitter: optional. If absent, sends
      all sections mixed

    Returns a JSON in the form:

    {
        "news":[{
    	    "id": "1",
    	    "wwwuser": "Iliana Olivié",
    	    "time": "201401101027",
	    "title": "¿El auge del resto? Apuntes sobre la presencia
	    global de América Latina, Asia y el Magreb y Oriente Medio",
            "link": "http://www.geographica.gs",
    	    "section": "Blog",
    	    "labels": [
                {"id": "1", "label": "IEPG"},
    	        {"id": "2", "label": "Economía"}]
        }]
    }

    TODO: revisar, devuelve unos id un poco raros
    """
    m = HomeModel()
    l = LabelModel()
    lang = request.args["lang"]
    section = int(request.args["section"]) if "section" in request.args else None

    try:
        labels = l.getLabels(lang)
        if section:
            if section in [1,2,3]:
                stuff = m.newStuffSections(lang, section)
            elif section==4:
                stuff = m.newStuffDocuments(lang)
            elif section==5:
                timeline = helpers.twitterGetLatestTweets()
                stuff = []
                for tweet in timeline:
                    stuff.append({
                        "id" : tweet.id,
                        "time" : tweet.created_at,
                        "title" : tweet.text,
                        "section" : "Twitter",
                        "labels" :[],
                        "wwwuser" : "@rielcano"
                    })
            else:
                e = ElcanoErrorBadNewsSection(section)
                return(jsonify(e.dict()))
        else:
            stuff = m.newStuffAll(lang)
    except ElcanoError as e:
        return(jsonify(e.dict()))

    for s in stuff:
        lab = []
        if s["labels"]!=[None]:
            for l in s["labels"]:
                for a in labels:
                    if str(a["id"])==str(l):
                        lab.append(a)

        s["labels"] = lab

    return(jsonify({"results": stuff}))


@app.route('/home/countrylist/<string:lang>', methods=['GET'])
def countryList(lang):
    """Returns the list of IEPG countries alphabetically ordered:

    /home/countrylist/en

    returns:

    {"results": [
    {"country_name": "Algeria"}, 
    {"country_name": "Angola"}, 
    {"country_name": "Argentina"}, ... ]}
    """
    m = HomeModel()
    return(jsonify({"results": m.countryList(lang)}))
