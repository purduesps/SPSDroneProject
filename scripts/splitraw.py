import cv2

if __name__ == "__main__":
    cap = cv2.VideoCapture('DataFootage3.MOV')
    framenum = 20000
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        cv2.imwrite('/media/zhukov/Commies/tagging/rawimg/ID{}.jpg'.format(str(framenum).zfill(10)),frame)
        print('/media/zhukov/Commies/tagging/rawing/ID{}.jpg'.format(str(framenum).zfill(10)))
        framenum += 1
