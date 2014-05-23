# coding=UTF8

"""

Maplex core

"""
import maplexmodel
import common.timelapse

def addName(name, description):
    """Adds a name. Returns reference ID to the new name."""
    m = maplexmodel.MaplexModel()
    id = m.newName(name, description)
    return(id)


def getNameFamilies():
    """Returns name families."""
    m = maplexmodel.MaplexModel()
    return(m.getNameFamilies())


def assignGeoentityName(idGeoentity, idName, idNameFamily, dateIn=None, dateOut=None):
    """Assign a name to a geoentity."""
    dateIn = common.timelapse.Time(dateIn) if dateIn else None
    dateOut = common.timelapse.Time(dateOut) if dateOut else None
        
    m = maplexmodel.MaplexModel()
    id = m.assignGeoentityName(idGeoentity, idName, idNameFamily, dateIn=dateIn, dateOut=dateOut)
    return(id)


def getGeoentities():
   """Returns geoentities."""
   m = maplexmodel.MaplexModel()
   return(m.getGeoentities())


def getNames(idNameFamily=None):
   """Returns names."""
   m = maplexmodel.MaplexModel()
   return(m.getNames(idNameFamily))


def getName(idName):
   """Returns name with ID idName."""
   m = maplexmodel.MaplexModel()
   return(m.getName(idName))


def getGeoentityNames(idGeoentity, idNameFamily):
    """Returns a list with all geoentity names corresponding to the given family."""
    m = maplexmodel.MaplexModel()
    return(m.getGeoentityNames(idGeoentity, idNameFamily))


def getIdGeoentityByName(name, idNameFamily):
    """Returns the idGeoentity for a name and ID name family."""
    m = maplexmodel.MaplexModel()
    return(m.getIdGeoentityByName(name, idNameFamily))

# TODO: redefine this method so it returns blocks whose existence is completely 
# within the lapse and make a difference on if the lapse is calculated by its members
# or the block itself
# Create a time topology: adjacency of timelapses, intersection of timelapses, containment of, etc...
# add after, before, coincident
# def getBlocks(timeLapseBlock=None, timeLapseMembers=None):
#     """Retrieves basic information about blocks."""
#     m = maplexmodel.MaplexModel()
#     return(m.getBlocks(timeLapseBlock, timeLapseMembers))


def getBlocks(timeLapseBlock=None, timeLapseMembers=None):
    """Retrieves basic information about blocks."""
    m = maplexmodel.MaplexModel()
    return(m.getBlocks(timeLapseBlock, timeLapseMembers))


def getBlockMembers(idGeoentityBlock, year=None):
    """Retrieves block members."""
    m = maplexmodel.MaplexModel()
    return(m.getBlockMembers(idGeoentityBlock, year))


def getGeoentityBlocks(idGeoentity, year=None):
    """Returns all blocks idGeoentity is in."""
    m = maplexmodel.MaplexModel()
    return(m.getGeoentityBlocks(idGeoentity, year))