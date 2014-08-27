# coding=UTF8

# --------------------------------
# Equidna Data Engine Core Classes
# --------------------------------

import numpy as np, hashlib, arrayops
from datetime import datetime, timedelta
import calendar

VAR_TYPE_CONTINUOUS = 0
VAR_TYPE_DISCRETE = 1

COPY_ALL = 0
COPY_GEOENTITIES = 1
COPY_TIMES = 2



class Geoentity(object):
    """TODO: Geoentity class."""
    pass



class Variable(object):
    """TODO: Variable class. Make stronger.

    TODO: accept names and descriptions and units as strings. Expand
    to the number of languages involved.

    - **filiation:** a dot separated filiation trace (IEPG.Economic.Energy);
    - **varType:** either VAR_TYPE_CONTINUOUS or VAR_TYPE_DISCRETE. It defaults to VAR_TYPE_CONTINUOUS;
    - **dataType:** a Numpy data type. Defaults to numpy.float64;
    - **languages:** list of language codes for names, descriptions and units. Must be declared for names, descriptions, and units to be added (["ES", "EN"]);
    - **names:** list of names in languages (["Energía", "Energy"]);
    - **descriptions:** list of descriptions (["Desc ES", "Desc EN"]);
    - **units:** list of units in languages (["Kw/h", "Kw/h"]);
    - **traits:** a dictionary with custom traits.

    """
    _filiation = None
    _languages = None
    _names = None
    _descriptions = None
    _units = None
    _varType = None
    _dataType = None
    _traits = None

    def __init__(self, filiation, varType=VAR_TYPE_CONTINUOUS, dataType=np.float_, 
                 languages=None, names=None, descriptions=None, 
                 units=None, traits=None):
        """Constructor. See general class description."""
        if filiation is None or filiation=="":
            raise EquidnaDataException("Bad filiation.")
        self._filiation = filiation.split(".")
        self._languages = languages

        if languages:
            for i in range(0, len(self._languages)):
                if names:
                    self._names = dict()
                    self._names[self._languages[i]] = names[i]
                if descriptions:
                    self._descriptions = dict()
                    self._descriptions[self._languages[i]] = descriptions[i]
                if units:
                    self._units = dict()
                    self._units[self._languages[i]] = units[i]

        self._varType = varType
        self._dataType = dataType
        self._traits = traits

    @property
    def filiation(self):
        """Variable filiation."""
        return(self._filiation)

    @property
    def languages(self):
        """Variable languages."""
        return(self._languages)

    @property
    def names(self):
        """Names."""
        return(self._names)

    @property
    def descriptions(self):
        """Descriptions."""
        return(self._descriptions)

    @property
    def units(self):
        """Variable units."""
        return(self._units)
    
    @property
    def varType(self):
        """Variable type: continuous / discrete."""
        return(self._varType)

    @property
    def dataType(self):
        """Data type (integer, etc.)."""
        return(self._dataType)
    
    @property
    def traits(self):
        """Variable traits."""
        return(self._traits)

    def __hash__(self):
        """Returns the hash."""
        return(int(hashlib.sha256(str(self._filiation)).hexdigest(), base=16))

    def __str__(self):
        """To string."""
        return(str(self._filiation))



class Time(object):
    """Time interval for Equidna."""
    start = None
    end = None

    def __init__(self, *timeInit):
        """Initializator. TODO: initialize months with str syntax '2013-01'."""
        if len(timeInit)==1:
            if "|" in timeInit[0]:
                self.start = self._getDatetime(timeInit[0].split("|")[0])
                self.end = self._getDatetime(timeInit[0].split("|")[1], lowerLimit=False, initialTime=self.start)
            else:
                self.start = self._getDatetime(timeInit[0])
                self.end = self._getDatetime(timeInit[0], lowerLimit=False, initialTime=self.start)
        if len(timeInit)==2:
            self.start = self._getDatetime(timeInit[0])
            self.end = self._getDatetime(timeInit[1], lowerLimit=False, initialTime=self.start)

        if self.start and self.end and self.start>self.end:
            self.start = None
            self.end = None

    def __div__(self, time):
        """Operator overload. Returns True if time is into the interval,
        extremes included. It gets either a datetime object or a
        string in ISO.

        """
        if not isinstance(time, Time):
            time = Time(time)

        if self.start and self.end and self.start<=time.start and time.end<=self.end:
            return(True)
        if self.start and self.end is None and self.start<=time.start:
            return(True)
        if self.start is None and self.end and time.end<=self.end:
            return(True)

        return(False)

    def __lt__(self, other):
        """Less than. Compares lower limit."""
        return self.start<other.start

    def __str__(self):
        """To str."""
        return("Time: "+str(self.start)+" | "+str(self.end))

    def _getDatetime(self, strptime, lowerLimit=True, initialTime=None):
        """Get the strptime."""
        if strptime=="" or strptime is None: return(None)


        # TODO: arreglar esto para que funcione con decrecimientos de año, contemplar las dos fechas a la vez, no hacer una análisis por separado.
        if any([x in strptime for x in ("Y","M","W","D","H","m","S")]) and initialTime:
            for x in ("Y","M","W","D","H","m","S"):
                parse = strptime.split(x)
                if len(parse)>1:
                    c = int(parse[0])
                    strptime = parse[1]
                    if x=="Y":
                        initialTime += datetime(initialTime.year+c, initialTime.month, initialTime.day, \
                                                initialTime.hour, initialTime.minute, initialTime.second) - \
                            initialTime
                    if x=="M":
                        if initialTime.month==12:
                            initialTime += datetime(initialTime.year+c, 1, initialTime.day, \
                                                    initialTime.hour, initialTime.minute, initialTime.second) - \
                                initialTime
                        else:
                            initialTime += datetime(initialTime.year, initialTime.month+c, initialTime.day, \
                                                    initialTime.hour, initialTime.minute, initialTime.second) - \
                                initialTime
                    if x=="W":
                        initialTime += timedelta(weeks=c)
                    if x=="D":
                        initialTime += timedelta(days=c)
                    if x=="H":
                        initialTime += timedelta(hours=c)
                    if x=="m":
                        initialTime += timedelta(minutes=c)
                    if x=="S":
                        initialTime += timedelta(seconds=c)

            return initialTime



        strp = "%Y-%m-%d %H:%M:%S"
        dt = strptime.split(" ")

        # Process date
        ymd = dt[0].split("-")
        if len(ymd)==2:
            if lowerLimit:
                ymd.append("01")
            else:
                days = calendar.monthrange(int(ymd[0]), int(ymd[1]))[1]
                ymd.append(str(days))
        if len(ymd)==1:
            if lowerLimit:
                ymd.extend(["01","01"])
            else:
                ymd.extend(["12","31"])

        # Process time
        if len(dt)==2:
            hms = dt[1].split(":")
            if len(hms)==2:
                if lowerLimit:
                    hms.append("00")
                else:
                    hms.append("59")
            if len(hms)==1:
                if lowerLimit:
                    hms.extend(["00","00"])
                else:
                    hms.extend(["59","59"])
        else:
            if lowerLimit:
                hms = ["00","00","00"]
            else:
                hms = ["23","59","59"]

        strptime = str(int(float(ymd[0])))+"-"+ymd[1]+"-"+ymd[2]+" "+hms[0]+":"+hms[1]+":"+hms[2]
        return(datetime.strptime(strptime, strp))

    def __hash__(self):
        """Get the hash."""
        return(int(hashlib.sha256(str(self)).hexdigest(), base=16))



class GeoVariableArray(object):
    """Data array for Equidna. Instantiate it with a list of geoentities and times.

    TODO: test if Numpy supports discrete values. 
    TODO: initialize time with a list of strings. 

    """
    __data = None
    __geoentity = None
    __time = None
    __variable = None

    def __init__(self, geoentity, time):
        """Initializator. Gets a list of geoentities and times to initialize
        the data array. TODO: initialize time with a list of strings.

        """
        self.__geoentity = [geoentity] if not isinstance(geoentity, list) else geoentity
        time = [time] if not isinstance(time, list) else time
        self.__time = [Time(x) for x in time if not isinstance(x, Time)]
        self.__time.extend([x for x in time if isinstance(x, Time)])
        self.__variable = []
        self.__data = np.empty((len(self.__geoentity), len(self.__time), 1))
        self.__data[:] = np.nan

    @property
    def geoentity(self):
        """Geoentity instances in the data matrix."""
        return(self.__geoentity)

    @property
    def time(self):
        """Times instances in the data matrix."""
        return(self.__time)

    @property
    def variable(self):
        """Variable instances in the data matrix."""
        return(self.__variable)

    @property
    def shape(self):
        """Returns dimensions of the data matrix. First item is Geoentity number, second Time, 
        and third Variable."""
        return self.__data.shape

    @property
    def size(self):
        """Returns size of data: Geoentity x Time x Variable."""
        return self.__data.size

    @property
    def data(self):
        """Data matrix. It's a Numpy ndarray object."""
        return(self.__data)

    def __getitem__(self, key):
        """Gets data."""

        print "Start : ", key, type(key)

        if isinstance(key, (slice, int)):
            return(self.__data[key])

        if len(key)>0:
            geo = self.__analyzeKeyGeoentity(key[0])
        else:
            geo = None
        if len(key)>1:
            time = self.__analyzeKeyTime(key[1])
        else:
            time = None
        if len(key)>2:
            var = self.__analyzeKeyVariable(key[2])
        else:
            var = None

        print "End : ", geo, time, var

        return(self.__data[geo,time,var])

    def __setitem__(self, key, value):
        """Set item."""
        geo = self.__analyzeKey(key[0], self.__geoentity)
        time = self.__analyzeKeyTime(key[1])
        var = self.__analyzeKey(key[2], self.__variable)

        self.__data[geo,time,var]=value

    def sort(self):
        unsorted = True
        while unsorted:
            unsorted = False
            i = 0
            while i<len(self.geoentity)-1:
                if self.geoentity[i]>self.geoentity[i+1]:
                    x = self.geoentity[i]
                    y = self.geoentity[i+1]
                    a = np.array(self.__data[i,:,:])
                    b = np.array(self.__data[i+1,:,:])
                    self.geoentity[i] = y
                    self.geoentity[i+1] = x
                    self.__data[i,:,:] = b
                    self.__data[i+1,:,:] = a
                    unsorted = True
                else:
                    i+=1

        unsorted = True
        while unsorted:
            unsorted = False
            i = 0
            while i<len(self.time)-1:
                if self.time[i]>self.time[i+1]:
                    x = self.time[i]
                    y = self.time[i+1]
                    a = np.array(self.__data[:,i,:])
                    b = np.array(self.__data[:,i+1,:])
                    self.time[i] = y
                    self.time[i+1] = x
                    self.__data[:,i,:] = b
                    self.__data[:,i+1,:] = a
                    unsorted = True
                else:
                    i+=1

    def __analyzeKeyTime(self, key):
        """Analyses a time key. TODO: this has a problem when asking for a
        non-existent year, like in data["US","2323","V0"]. FIX!

        """

        print "KeyTime : ",key, type(key)

        if callable(key):
            out = ()
            for i in range(0, len(self.__time)):
                if key(self.__time[i]):
                    out+=(i,)
            return out
        if isinstance(key, (str, Time)):
            out = ()
            for i in range(0, len(self.__time)):
                if self.__time[i]/key:
                    out+=(i,)
            return out
        if isinstance(key, tuple):
            out = ()
            for i in key:
                out+=(self.__analyzeKeyTime(i),)
            return out
        if isinstance(key, (int, slice)):
            return key
        
    def __analyzeKeyGeoentity(self, key):
        """Analyses key for a given dimension."""

        print "KeyGeoentity : ", key, type(key)

        if isinstance(key, str):
            return(self.geoentity.index(key))
        if isinstance(key, tuple):
            out = ()
            for i in key:
                out+=(self.__analyzeKeyGeoentity(i),)
            return(out)
        if isinstance(key, (int, slice)):
            return(key)

    def __analyzeKeyVariable(self, key):
        """Analyses key for a given dimension."""

        print "KeyVariable : ", key, type(key)

        if isinstance(key, str):
            return(self.variable.index(key))
        if isinstance(key, tuple):
            out = ()
            for i in key:
                out+=(self.__analyzeKeyVariable(i),)
            return(out)
        if isinstance(key, (int, slice)):
            return(key)

    def addGeoentity(self, geoentity, data=None):
        """Adds new geoentities to the geoentity dimension. Geoentity can be a
        string or a list of strings. WARNING! Values added to the
        matrix are random! Initialize true values inmediatly!

        TODO: provide data matrix.

        """
        geoentity = [geoentity] if not isinstance(geoentity, list) else geoentity
        data = [data] if data and not isinstance(data[0], list) else data
        
        for i in range(0, len(geoentity)):
            if geoentity[i] not in self.geoentity:
                s = self.shape
                if not data:
                    dataA = np.empty((1,s[1],s[2]))
                    dataA[:] = np.nan
                else:
                    dataA = data[i]

                self.__data = np.append(self.__data, np.array(dataA).reshape(1, s[1], s[2]), 
                                        axis=0)
                self.__geoentity.append(geoentity[i])

    def addTime(self, time, data=None):
        """Adds new times to the time dimension. time can be a Time or a list
        of Time. WARNING! Values added to the matrix are random!
        Initialize true values inmediatly!

        """
        time = [time] if not isinstance(time, list) else time
        data = [data] if data and not isinstance(data[0], list) else data
        
        for i in range(0, len(time)):
            s = self.shape
            if not data:
                dataA = np.empty((s[0],1,s[2]))
                dataA[:] = np.nan
            else:
                dataA = data[i]
            self.__data = np.append(self.__data, np.array(dataA).reshape(s[0], 1, s[2]), 
                                    axis=1)
            self.__time.append(Time(time[i]) if not isinstance(time[i], Time) else time[i])

    def addVariable(self, name, darray):
        """Adds a new variable to the variables dimension. Variables can be a
        string or a list of strings. darray is a unidimensional numpy
        ndarray or a bidimensional one. There must be enough data to
        fit the size of the array.

        TODO: check other addXXX methods and reharse this. CRAP!

        """
        name = [name] if not isinstance(name, list) else name
        darray = [darray] if not isinstance(darray, list) else darray
        if len(name)!=len(darray):
            raise EquidnaDataException("Variable names and matrices number mismatch.")

        for i in range(0, len(name)):
            if name[i] in self.variable:
                continue

            if darray[i].size!=self.__data[:,:,0].size:
                raise EquidnaDataException("Data and GeoVariableArray must have the same size.")

            s = self.shape
            self.__variable.append(name[i])
            if len(self.__variable)==1:
                self.__data = darray[i].reshape((s[0],s[1],1))
            else: 
                self.__data = np.append(self.__data, darray[i].reshape((s[0],s[1],1)), axis=2)

    def copyStructure(self, copy=COPY_ALL):
        """Returns a GeoVariableArray with the same geoentities and times."""
        geoentity = []
        time = []

        if copy==COPY_ALL or copy==COPY_GEOENTITIES:
            geoentity = self.geoentity
        if copy==COPY_ALL or copy==COPY_TIMES:
            time = self.time

        return GeoVariableArray(geoentity, time)

    def merge(self, geoVariableArray):
        """Merges two GeoVariableArrays. If a variable is present in the
        second GeoVariableArray that is present in the first one it's
        omitted.

        """
        diffGeoentityAB = arrayops.arraySubstraction(self.geoentity, geoVariableArray.geoentity)
        diffGeoentityBA = arrayops.arraySubstraction(geoVariableArray.geoentity, self.geoentity)
        self.addGeoentity(diffGeoentityBA)
        geoVariableArray.addGeoentity(diffGeoentityAB)

        diffTimeAB = arrayops.arraySubstraction(self.time, geoVariableArray.time)
        diffTimeBA = arrayops.arraySubstraction(geoVariableArray.time, self.time)
        self.addTime(diffTimeBA)
        geoVariableArray.addTime(diffTimeAB)

        self.sort()
        geoVariableArray.sort()

        diffVariable = arrayops.arraySubstraction(geoVariableArray.variable, self.variable)
        self.addVariable(diffVariable, [geoVariableArray[:,:,x] for x in diffVariable])



class EquidnaDataException(Exception):
    """Exception for Equidna data."""
    _message = ""

    def __init__(self, message):
        self._message = message
    
    def __str__(self):
        return("EquidnaDataException: "+self._message)
