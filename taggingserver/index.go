package main

import (
        "net/http"
//        "log"
        "os"
        "fmt"
        "gopkg.in/mgo.v2"
        "bytes"
        "gopkg.in/mgo.v2/bson"
        "strconv"
)
type BB struct {
    ID int
    w []float64
    h []float64
    Xpos []float64
    Ypos []float64
}
const imgdir = "./rawimg"
func parseToJson(body []byte)( *BB) {
    bb := new(BB)
    tr := bytes.Trim(body,"\x00")
    sp := bytes.Split(tr, []byte("&"))
    for _,by := range sp{
        chunks := bytes.Split(by,[]byte("="))
        key := string(chunks[0])
        if  key == "ID"{
                bb.ID ,_ = strconv.Atoi(string(chunks[1]))
        } else if key == "Xpos"{
                xs := bytes.Split(chunks[1],[]byte("%2C"))
                for _,x := range xs {
                        xf,_ :=strconv.ParseFloat(string(x),64)
                        bb.Xpos = append(bb.Xpos,xf)
                }
        } else if key == "Ypos"{
                xs := bytes.Split(chunks[1],[]byte("%2C"))
                for _,x := range xs {
                        xf,_ :=strconv.ParseFloat(string(x),64)
                        bb.Ypos = append(bb.Ypos,xf)
                }
        } else if key == "widths" {
                xs := bytes.Split(chunks[1],[]byte("%2C"))
                for _,x := range xs {
                        xf,_ :=strconv.ParseFloat(string(x),64)
                        bb.w = append(bb.w,xf)
                }
        } else if key == "heights" {
                xs := bytes.Split(chunks[1],[]byte("%2C"))
                for _,x := range xs {
                        xf,_ :=strconv.ParseFloat(string(x),64)
                        bb.h = append(bb.h,xf)
                }
        } else {
                panic("NO KEY")
        }
    }
    return bb
}
func postresp(w http.ResponseWriter, r * http.Request) {
        bdy := make([]byte,10000)
        r.Body.Read(bdy)
        taggedData := parseToJson(bdy)

        session, _ := mgo.Dial("localhost")
        defer session.Close()
        session.SetMode(mgo.Monotonic, true)
        c := session.DB("DroneTags").C("people")

        exist := new(BB)
        //c.Update(bson.M{"id":taggedData.ID},taggedData)
        change := mgo.Change{
                Update: bson.M{"$set": bson.M{"id":taggedData.ID,"xpos":taggedData.Xpos,"ypos":taggedData.Ypos,"h":taggedData.h,"w":taggedData.w}},
                Upsert: true,
                ReturnNew: true,
        }
        c.Find(bson.M{"id":taggedData.ID}).Apply(change,exist)
        fmt.Printf("%v;%v;\n",r.RemoteAddr,len(taggedData.h))
        http.ServeFile(w, r, "./static/thanks.html")
}

func selectImg(dirname string)(ID string) {
        session, _ := mgo.Dial("localhost")
        defer session.Close()
        c := session.DB("DroneTags").C("people")
        imgnum := 0
        exist := new(BB)
        found := c.Find(bson.M{"id":imgnum}).One(exist)
        _, err := os.Stat(fmt.Sprintf("%v/ID0%09v.jpg",dirname,imgnum));
        for  os.IsNotExist(err) || found == nil{
                imgnum += 1
                found = c.Find(bson.M{"id":imgnum}).One(exist)
                _, err = os.Stat(fmt.Sprintf("%v/ID0%09v.jpg",dirname,imgnum));
        }
        ret := strconv.Itoa(imgnum)
        return ret
}
func imgresp(w http.ResponseWriter, r * http.Request) {
        imgid := selectImg(imgdir)
        cookie1 := &http.Cookie{Name: "ID", Value: imgid, HttpOnly: false}
        http.SetCookie(w, cookie1)
        w.Header().Set("Cache-Control","no-cache, no-store, must-revalidate")
        w.Header().Set("Pragma","no-cache")
        w.Header().Set("Expires","0")
        http.ServeFile(w, r, fmt.Sprintf("%v/ID0%09v.jpg",imgdir,imgid))
}

func main() {
        http.Handle("/", http.FileServer(http.Dir("./static")))
        http.Handle("/return", http.HandlerFunc(postresp))
        http.Handle("/frame.jpg", http.HandlerFunc(imgresp))
        http.ListenAndServe(":3000", nil)
}
