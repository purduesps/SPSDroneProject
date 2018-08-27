import numpy as np
from peopledata import PersonData, PeopleData, savepeopledata

if __name__ == "__main__":
    NUM_PEOPLE = 50
    DEFAULT_YPOS = np.array(list(range(18000)))
    DEFAULT_XPOS = np.array(list(range(18000)))
    DEFAULT_DX = np.array([i/0.05 for i in DEFAULT_XPOS])
    DEFAULT_DY = np.array([i/0.05 for i in DEFAULT_YPOS])

    p = PeopleData()
    for i in range(NUM_PEOPLE):
        person = PersonData(i,
                            ypositions=DEFAULT_YPOS + 1,
                            xpositions=DEFAULT_XPOS,
                            yvelocities=DEFAULT_DX,
                            xvelocities=DEFAULT_DY)
        p.append(person)

    print(p)
    print(p.stateS(3))
    print(p.stateT(0.03))
    savepeopledata("picklefile", p)

