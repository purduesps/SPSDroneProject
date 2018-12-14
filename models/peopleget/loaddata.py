from pickle import load
from peopledata import PersonData, PeopleData, getdeopledata,savepeopledata


class mymodel(object):
    def __init__(self,param=4):
        self.dt = 0.05
        self.parameter = 5
        self.parameter2 = param

    def print_parameters(self):
        print(self.parameter)
        print(self.parameter2)

    def propagate(self, startstep, peopledata,nsteps):
        pass


if __name__ == "__main__":
    p = PeopleData()
    p.load("trajectories2.json")
    savepeopledata("peopledata2.pkl",p)
