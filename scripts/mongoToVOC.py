import sys
from os import listdir, mkdir, getcwd
from os.path import isfile, join
import shutil
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element

from pymongo import MongoClient


def indent(elem, level=0):
  i = "\n" + level*"  "
  if len(elem):
    if not elem.text or not elem.text.strip():
      elem.text = i + "  "
    if not elem.tail or not elem.tail.strip():
      elem.tail = i
    for elem in elem:
      indent(elem, level+1)
    if not elem.tail or not elem.tail.strip():
      elem.tail = i
  else:
    if level and (not elem.tail or not elem.tail.strip()):
      elem.tail = i

class DroneTags(object):
    def __init__(self, imgdir, defaultxml="default.xml"):
        self.picdir = imgdir
        self.client =MongoClient()['DroneTags']['people']
        self.tags = self.client.find({}, {'id': 1, '_id': 1})
        self.imgs = [join(imgdir, f) for f in listdir(imgdir) if isfile(join(imgdir, f))]
        self.defTree = ET.parse(defaultxml)
        self.defTree.getroot().remove(self.defTree.find("object"))

    def VOCify(self,outputdir,imgh=540,imgw=960):
        untaggedImg = []
        noimgTag = []
        train_img_dir = "{}/{}".format(outputdir, "train_img")
        train_annot_dir = "{}/{}".format(outputdir, "train_annot")
        valid_img_dir = "{}/{}".format(outputdir, "valid_img")
        valid_annot_dir = "{}/{}".format(outputdir, "valid_annot")
        shutil.rmtree(outputdir)
        mkdir(outputdir)
        mkdir(train_img_dir)
        mkdir(train_annot_dir)
        mkdir(valid_img_dir)
        mkdir(valid_annot_dir)
        for tag in self.tags:
            newtag = self.defTree
            imgname = "{}/ID{}.jpg".format(self.picdir, str(tag["id"]).zfill(10))
            xmlname = "{}/ID{}.xml".format(train_annot_dir, str(tag["id"]).zfill(10))
            if imgname not in self.imgs:
                untaggedImg.append(imgname)
                break
            shutil.copyfile(imgname, train_img_dir + "/ID{}.jpg".format(str(tag["id"]).zfill(10)))
            tagdata = self.client.find({'_id': tag['_id']}).next()
            print(tagdata['id'])

            newtag.find("folder").text = "train_img"
            newtag.find("filename").text = "ID{}.jpg".format(str(tag["id"]).zfill(10))
            newtag.find("path").text = train_img_dir + "/ID{}.jpg".format(str(tag["id"]).zfill(10))
            newtag.find("size").find("width").text = str(imgw)
            newtag.find("size").find("height").text = str(imgh)

            for i in range(len(tagdata["xpos"])):
                newobj = Element("object")
                newobj.append(Element("name"))
                newobj.append(Element("pose"))
                newobj.append(Element("truncated"))
                newobj.append(Element("difficult"))

                newobj.find("name").text = "person" + str(i)
                newobj.find("pose").text = "unspecified"
                newobj.find("truncated").text = "0"
                newobj.find("difficult").text = "0"
                newobj.find("name").text = "person" + str(i)

                BB = Element("bndbox")
                BB.append(Element("xmin"))
                BB.append(Element("ymin"))
                BB.append(Element("xmax"))
                BB.append(Element("ymax"))
                newobj.append(BB)

                BB.find("xmin").text = str(tagdata["xpos"][i] - tagdata["w"][i]/2)
                BB.find("ymin").text = str(tagdata["ypos"][i] - tagdata["h"][i]/2)
                BB.find("xmax").text = str(tagdata["xpos"][i] + tagdata["w"][i]/2)
                BB.find("ymax").text = str(tagdata["ypos"][i] + tagdata["h"][i]/2)
                indent(newobj)
                newtag.getroot().append(newobj)

            newtag.write(xmlname, xml_declaration=True, method="xml")

        return untaggedImg


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python mongoToVOC <imagedir> <database>")
    tgs = DroneTags("./tagging/rawimg")

    untagged = tgs.VOCify(getcwd() + "/peopledataset")
    tgs.defTree.write("foo.xml", xml_declaration=True, method="xml")


