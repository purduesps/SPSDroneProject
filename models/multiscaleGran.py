from scipy.spatial import distance
from peopleget.peopledata import PersonData, PeopleData, getdeopledata
from math import pow, cos, atan2, sin
import numpy as np
import timeit
import sys
from enum import Enum
sys.path.insert(0, "peopleget")


class Boundries(Enum):
    MINY = 1
    MAXX = 2
    MAXY = 3
    MINX = 4


class SimpleRules(object):
    def __init__(self,
                 t=1,
                 phi=1,
                 m_i=1,
                 d_max=1,
                 dt=0.05,
                 vi0=1,
                 obstspace=None
                 ):
       
        self.dt = dt
        self.t = t
        self.phi = phi
        self.r_i = m_i/320
        self.d_max = d_max
        self.obstSpace = obstspace  # This is a field size array of booleans that define obstacles
        self.angcheck = 100
        self.vi0 = vi0

    def print_parameters(self):
        print("dT: ", self.dt)
        print("T: ", self.t)
        print("Phi: ", self.phi)
        print("D max: ", self.d_max)

    def spaceToHit(self, space, angle, actpos):
        hitpoints = []
        for x in range(space.shape[0]):
            for y in range(space.shape[1]):
                if space[x, y]:
                    newx = x - actpos[0]
                    newy = y - actpos[1]
                    newx = newx*cos(angle) - newy*sin(angle)
                    newy = newx*sin(angle) + newy*cos(angle)
                    hitpoints.append((newx, newy))
        return hitpoints

    def Fa(self, angles, pos, obsSpace):
        fas = []
        for angle in angles:
            obst = self.spaceToHit(obsSpace, angle, pos)
            hits = [obs for obs in obst if abs(obs[1]) < self.r_i]
            neardist = hits[0][0]
            for obs in hits:
                if obs[0] < neardist:
                    neardist = obs[0]
            fas.append(neardist)

        return angles

    def Vdes(self, v0, dh):
        if v0 > dh/self.t:
            return dh/self.t
        else:
            return v0

    def Da(self, alpha, alpha_0, fa):
        return [pow(self.d_max, 2) + pow(fa_i, 2) - 2*self.d_max*fa_i*cos(alpha_0-alph) for alph, fa_i in zip(alpha, fa)]

    # If the disappear, their destination is where they disappeared.
    # If they walked off an edge, their dest is closest to edge
    def getTerm(self, person, space):
        lastpos = (person.xpos[-1], person.ypos[-1])
        edgethresh = 10
        if lastpos[0] > space[0] - edgethresh:
            return Boundries.MAXX

        if lastpos[0] < edgethresh:
            return Boundries.MINX

        if lastpos[1] > space[1] - edgethresh:
            return Boundries.MAXY

        if lastpos[1] < edgethresh:
            return Boundries.MINY

        return lastpos

    def getDest(self, dest, space):
        if type(dest[1]) == Boundries:
            xPos = dest[0][0]
            yPos = dest[0][1]
            if dest[1] == Boundries.MAXX:
                return space[0], yPos
            if dest[1] == Boundries.MAXY:
                return xPos, space[1]
            if dest[1] == Boundries.MINX:
                return space[0], 0
            if dest[1] == Boundries.MINY:
                return 0, space[1]
        else:
            return dest

    def propagate(self, startstep, peopledata, nsteps):
        people = [(p[1], p[2]) for p in peopledata.stateS(startstep)]
        peopleN =[(p[1], p[2]) for p in peopledata.stateS(startstep + 1)]
        orientations = [atan2(pn[1]-p[1], pn[0]-p[0]) for p, pn in zip(people, peopleN)]
        termBoundries = [self.getTerm(p, self.obstSpace.shape) for p in peopledata.people]
        '''
        boundaries are defined as such
                MaxY     (maxX,maxY)
        -------------------
        |                 |
        |                 |
 Minx   |      field      | MaxX   pi rads <--o--> 0 rads
        |                 |              
        |                 |
        -------------------
     (0,0)       MinY
        '''
        for n in range(nsteps):

            tStamp = timeit.default_timer()
            dests = [self.getDest(term, self.obstSpace.shape) for term in zip(people, termBoundries)]
            desorientations = [atan2(dest[1]-pos[1], dest[0]-dest[0]) for pos, dest in zip(people, dests)]
            fullObsSpace = np.full((640, 480), False, dtype=bool)

            for p in people:
                for i in range(int(max(p[0]-self.r_i, 0)), int(min(p[0]+self.r_i, self.obstSpace.shape[0]-1))):
                    for j in range(int(max(p[1]-self.r_i, 0)), int(min(p[1]+self.r_i, self.obstSpace.shape[0]-1))):
                        if distance.euclidean(p[0], (i, j)) < self.r_i:
                            fullObsSpace[i, j] = True
            fullObsSpace = np.logical_or(fullObsSpace, self.obstSpace)

            alpha_des = []
            d_h = []
            for p, an, dAn in zip(people, orientations, desorientations):
                angles = np.linspace(an-self.phi, an+self.phi, self.angcheck)
                fa = self.Fa(angles, p, fullObsSpace)
                da = self.Da(angles, dAn, fa)
                alpha_des.append(angles[da.index(min(da))])
                d_h.append(fa[da.index(min(da))])
            v_des = [min(self.vi0, dh/self.t) for dh in d_h]
            people = [(p[0]+cos(alpha)*v*self.t, p[1]+sin(alpha)*v*self.t) for p, alpha, v in zip(people, alpha_des,v_des)]
            orientations = alpha_des
            print("One Step took: {} Minutes".format((timeit.default_timer()-tStamp)/60.0))
        return [(p[0], p[1], v*cos(o), v*sin(o)) for p, v, o in zip(people, v_des, orientations)]

if __name__ == "__main__":
    p = getdeopledata("picklefile")
    print(p)
    m = SimpleRules(m_i=360*20, obstspace=np.full((640, 480), False, dtype=bool))
    m.print_parameters()
    print(m.propagate(0, p, 10))
