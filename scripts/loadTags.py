from pymongo import MongoClient
import numpy as np
import cv2
from os import listdir
from os.path import isfile, join


class DroneTags(object):
    def __init__(self, imgdir,numrows=5,numcols=8,batchsize = 1000,BB = 10):
        self.picdir = imgdir
        self.tags = MongoClient()['DroneTags']['people'].find({})
        self.imgs = [join(imgdir, f) for f in listdir(imgdir) if isfile(join(imgdir, f))]
        self.ncols = numcols
        self.nrows = numrows
        self.imshape = cv2.imread(self.imgs[0]).shape
        self.bsize = batchsize
        self.nBB = BB

    def __iter__(self):
        return self

    def VOCify(self):

    def data(self):
        rettag = np.zeros((self.bsize, self.nrows, self.ncols, 3*self.nBB), dtype=np.float32)
        imgs = np.zeros((self.bsize, self.imshape[0], self.imshape[1], self.imshape[2]), dtype=np.float32)
        for Bnum in range(self.bsize):
            tag = self.tags.next()
            imgname = "{}ID{}.jpg".format(self.picdir, str(tag["id"]).zfill(10))
            if imgname not in self.imgs:
                raise Exception("CANT FIND IMAGE FOR TAG {}".format(str(tag["id"])))
            img = cv2.imread(imgname)
            xtags = list(map(lambda x: x/self.imshape[1], tag["xpos"]))
            ytags = list(map(lambda y: y/self.imshape[0], tag["ypos"]))

            ptrarr = [0]*self.nrows*self.ncols
            for i in range(len(xtags)):
                col = int(xtags[i]*self.ncols)
                row = int(ytags[i]*self.nrows)
                relX = xtags[i] - (col/self.ncols)
                relY = ytags[i] - (row/self.nrows)
                ind = ptrarr[self.ncols*row + col]

                rettag[Bnum, row, col, ind] = relX
                rettag[Bnum, row, col, ind+1] = relY
                rettag[Bnum, row, col, ind+2] = 1

                ptrarr[self.ncols*row + col] += 3
            np.copyto(imgs[Bnum, :, :, :], img[:, :, :].astype(np.float32, copy=True))

        return {"frame": imgs}, rettag

    def __next__(self):
        return self.data()

if __name__ == "__main__":
    d = DroneTags("./tagging/rawimg/")
    for im, tns in d:
        k = cv2.waitKey(30)
        r = 2
        c = 3
        for j in range(0, 30, 3):
            X = tns[1, r, c, j]
            Y = tns[1, r, c, j+1]
            cv2.circle(im[1, :, :, :], (int((X+c/d.ncols)*d.imshape[1]), int((Y+r/d.nrows)*d.imshape[0])), 6, (0, 255, 0), -1)

        cv2.imshow('frame', im[1, :, :, :])
        if k == 97:
            break
