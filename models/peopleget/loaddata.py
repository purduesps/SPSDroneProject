from pickle import load
from peopledata import PersonData, PeopleData, getdeopledata


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
    p = getdeopledata("picklefile")
    m = mymodel(param=5)
    m2 = mymodel(param=6)
    m.print_parameters()
    m2.print_parameters()
    data_at_3step = p.stateS(3)
    print(data_at_3step)
