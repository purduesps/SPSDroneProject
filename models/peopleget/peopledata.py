import numpy as np
from pickle import dumps, loads
import json
import zlib


class PeopleData(object):
    def __init__(self, deltat = 0.05):
        self.dt = deltat
        self.people = []

    def append(self, val):
        if type(val) != PersonData:
            raise TypeError("CAN ONLY APPEND PEOPLE")
        self.people.append(val)

    def __str__(self):
        return "Number of People {}".format(len(self.people))

    def stateS(self,stepnum):
        if type(stepnum) != int:
            raise TypeError("STEPNUM MUST BE AN INTEGER")
        existing = [ p for p in self.people if p.timestart < stepnum and p.timeend > stepnum]
        return [(p.ID, p.xpos[stepnum - p.timestart],
                       p.ypos[stepnum - p.timestart],
                       p.dx[stepnum - p.timestart], 
                       p.dy[stepnum - p.timestart]) for p in existing]

    def stateT(self, time):
        return self.stateS(int(time/self.dt))
    def load(self,fname):
        with open(fname,"r") as fh:
                data = json.load(fh)
        for ids, poss in data.items():
            numframes = poss[-1]['fnum'] - poss[0]['fnum']
            startframe = poss[0]['fnum']
            xpos = np.zeros(numframes,dtype=np.float64)
            ypos = np.zeros(numframes,dtype=np.float64)
            posidx = 0
            for fnum in range(numframes):
                if poss[posidx]['fnum'] == fnum + startframe:
                    xpos[fnum] = poss[posidx]['x']
                    ypos[fnum] = poss[posidx]['y']
                    posidx+=1
                else:
                    xpos[fnum] = -1
                    ypos[fnum] = -1
            xpos[numframes - 1] = poss[-1]['x']
            ypos[numframes - 1] = poss[-1]['y']
            for fnum in range(numframes):
                if xpos[fnum] == -1:
                    upto = fnum
                    while xpos[upto] == -1:
                        upto += 1

                    prevposX = xpos[fnum-1]
                    nextposX = xpos[upto]
                    v = prevposX + (nextposX-prevposX)/(upto-fnum)
                    for i in range(fnum,upto):
                        xpos[i] = v 
                        v += (nextposX-prevposX)/(upto-fnum)

                    prevposY = ypos[fnum-1]
                    nextposY = ypos[upto]
                    v = prevposY + (nextposY-prevposY)/(upto-fnum)
                    for i in range(fnum,upto):
                        ypos[i] = v 
                        v += (nextposY-prevposY)/(upto-fnum)
            
            xvel = postovelo(xpos)
            yvel = postovelo(ypos)
            self.append(PersonData(int(float(ids)),
                                   tStart=startframe,
                                   xpositions = xpos,
                                   ypositions = ypos,
                                   xvelocities = xvel,
                                   yvelocities = yvel))
            #print("Xpos",xpos)
            #print("Ypos",ypos)
            #print("Xvel",xvel)
            #print("Yvel",yvel)
def postovelo(poss):
    velos = np.zeros(len(poss),dtype=np.float64)
    coll = 5 
    for i in range(1,coll):
        weightedvelos = [v/(1 + i - previdx) for previdx,v in enumerate(velos[:i])]
        weightedvelos.append(poss[i] - poss[i-1])
        velos[i] = sum(weightedvelos)/len(weightedvelos)
    for i in range(coll,len(poss)):
        weightedvelos = [v/(1 + i - previdx) for previdx,v in enumerate(velos[i-coll:i])]
        weightedvelos.append(poss[i] - poss[i-1])
        velos[i] = sum(weightedvelos)/len(weightedvelos)
    return velos
class PersonData(object):
    def __init__(self, IDnum,
                 tStart = 0,
                 ypositions=np.zeros(1000, dtype=np.float64),
                 xpositions =np.zeros(1000, dtype=np.float64),
                 xvelocities=np.zeros(1000, dtype=np.float64),
                 yvelocities =np.zeros(1000, dtype=np.float64)):
        self.ID = IDnum
        self.numdata = len(ypositions)
        self.timestart = tStart
        self.timeend = tStart + self.numdata

        if any(type(arg) != np.ndarray for arg in [ypositions, xpositions, ypositions, xvelocities]):
            raise TypeError("ALL INPUTS NEED TO BE NUMPY ARRAYS")

        self.ypos = ypositions
        self.xpos = xpositions
        self.dy = yvelocities
        self.dx = xvelocities

    def getDest(self):
        raise Exception("IMPLEMENT THE GET DESDT FUNCTION IN YOUR MODEL")


def savepeopledata(filename,people):
    if type(people) != PeopleData:
        return TypeError("YOUR INPUT ISNT A PEOPLEDATA")
    with open(filename, "wb") as fh:
        fh.write(dumps(people))


def getdeopledata(filename):
    with open(filename, "rb") as fh:
        p = loads(fh.read())
    return p


def plotpeople(people):
    if type(people) != PeopleData:
        return TypeError("YOUR INPUT ISNT A PEOPLEDATA")
