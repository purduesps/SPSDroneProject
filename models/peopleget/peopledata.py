import numpy as np
from pickle import dumps, loads
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
        return [(p.ID, p.xpos[stepnum], p.ypos[stepnum], p.dx[stepnum], p.dy[stepnum]) for p in self.people]

    def stateT(self, time):
        return self.stateS(int(time/self.dt))


class PersonData(object):
    def __init__(self, IDnum,
                 ypositions=np.zeros(1000, dtype=float),
                 xpositions =np.zeros(1000, dtype=float),
                 xvelocities=np.zeros(1000, dtype=float),
                 yvelocities =np.zeros(1000, dtype=float)):
        self.ID = IDnum
        if ~(len(ypositions) == len(xpositions) == len(yvelocities) == len(xvelocities)):
            raise ValueError("ALL STATE LISTS MUST BE THE SAME LENGTH")

        self.numdata = len(ypositions)

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
