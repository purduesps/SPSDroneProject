from pickle import load
import functools
import cv2
from CV import pntCld

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


with open("pntcld.pkl", "rb") as fh:
    pntcld = load(fh).vals

comp = chunks(pntcld, 5)
lowerdim = [functools.reduce(lambda x, a: x + a, c) for c in comp]
for i in lowerdim:
    for pnt in i:
        print("Point: ({},{}) Size: {}".format(pnt.pt[0], pnt.pt[1], pnt.size))
