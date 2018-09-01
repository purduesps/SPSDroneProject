from scipy.spatial import distance
from models.peopleget.peopledata import PersonData, PeopleData, getdeopledata
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

    # def spaceToHit(self, space, angle, actpos):
    #     coords = np.array(np.where(space)).T - actpos
    #
    #     rot_mat = np.array([[cos(angle), -sin(angle)], [sin(angle), cos(angle)]])
    #     hitpoints = np.matmul(rot_mat, coords.T).T
    #
    #     return hitpoints

    def Fa(self, angles, pos, obsSpace):
        fas = []
        coords = (np.array(np.where(obsSpace)).T - pos).T
        c, s = np.cos(angles), np.sin(angles)
        rots = np.array([[c, -s], [s, c]]).transpose((2, 0, 1))
        for rot_mat in rots:
            # rot_mat = np.array([[cos(angle), -sin(angle)], [sin(angle), cos(angle)]])
            # obst = self.spaceToHit(obsSpace, angle, pos)
            obst = np.matmul(rot_mat, coords)
            hits = obst[0, ((np.abs(obst[1]) < self.r_i) & (obst[0] > 0))]

            neardist = np.amin(hits)
            fas.append(neardist)

        return np.array(fas)

    def Da(self, alpha, alpha_0, fa):
        return self.d_max**2 + fa**2 - 2*self.d_max*fa*np.cos(alpha_0 - alpha)
        # return [self.d_max**2 + fa_i**2 - 2*self.d_max*fa_i*cos(alpha_0-alph) for alph, fa_i in zip(alpha, fa)]

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
        people = np.array([(p[1], p[2]) for p in peopledata.stateS(startstep)])
        peopleN =np.array([(p[1], p[2]) for p in peopledata.stateS(startstep + 1)])

        ds = peopleN - people

        orientations = np.arctan2(ds[:,1], ds[:,0])
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
            yc, xc = np.ogrid[:640, :480]
            for p in people:
                distsq = (xc - p[0])**2 + (yc - p[1])**2
                circ_mask = distsq <= self.r_i**2

                fullObsSpace[circ_mask] = True
            print('generating obstacle map from people\t: {} s'.format(timeit.default_timer()-tStamp))

            fullObsSpace = np.logical_or(fullObsSpace, self.obstSpace)

            alpha_des = []
            d_h = []
            tsi = timeit.default_timer()
            for p, an, dAn in zip(people, orientations, desorientations):
                angles = np.linspace(an-self.phi, an+self.phi, self.angcheck)
                fa = self.Fa(angles, p, fullObsSpace)
                da = self.Da(angles, dAn, fa)

                min_da = np.argmin(da)

                alpha_des.append(da[min_da])
                d_h.append(fa[min_da])
            print('main loop\t: {} s'.format(timeit.default_timer()-tsi))
            alpha_des = np.array(alpha_des)
            d_h = np.array(d_h)

            tsi = timeit.default_timer()
            v_des = np.minimum(d_h/self.dt, self.vi0)
            v_des_v = v_des * np.array([np.cos(alpha_des), np.sin(alpha_des)])

            people = people + v_des_v.T * self.dt
            orientations = alpha_des
            self.t += self.dt
            print('the rest: {} s'.format(timeit.default_timer() - tsi))
            print("One Step took: {} s".format((timeit.default_timer()-tStamp)))
        return [(p[0], p[1], v*cos(o), v*sin(o)) for p, v, o in zip(people, v_des, orientations)]

if __name__ == "__main__":
    p = getdeopledata("picklefile")
    print(p)
    m = SimpleRules(m_i=360*20, obstspace=np.full((640, 480), False, dtype=bool))
    m.print_parameters()
    print(m.propagate(0, p, 10))
