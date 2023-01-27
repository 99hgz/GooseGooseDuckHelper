from keyandmouse import *
import pyautogui
from win32gui import *
from PIL import ImageGrab
import numpy
import cv2,time
from queue import Queue
import random
import math,os
os.system("chcp 65001 && cls")

isHost = 0
mapImg = windowTopLeft = windowLowerRight = 0
currentTaskId = 0

#游戏图像处理相关
def screenShotInit():
    global mapImg , windowTopLeft , windowLowerRight
    window = FindWindow(0, "Goose Goose Duck")
    mapImg = cv2.imread("./img/minimap_540p.png")
    windowBox = GetClientRect(window)
    windowTopLeft = ClientToScreen(window,(0,0))
    windowLowerRight = ClientToScreen(window,(windowBox[2],windowBox[3]))
def getMyPos():
    if True:
        image = ImageGrab.grab((*windowTopLeft,*windowLowerRight))
        #当不在游戏中返回-1
        if(image.getpixel((1187,541)) == (255,255,255)):
            return -1
        
        cropped = image.crop((1144, 66, 1144 + 70, 66 + 70)) 
        template = cv2.cvtColor(numpy.array(cropped), cv2.COLOR_RGB2BGR)
        theight, twidth = template.shape[:2]
        result = cv2.matchTemplate(mapImg,template,cv2.TM_SQDIFF_NORMED)
        cv2.normalize( result, result, 0, 1, cv2.NORM_MINMAX, -1 )
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        x=min_loc[0]+twidth//2
        y=min_loc[1]+theight//2
        return (x,y)
def taskTextInit():
    global taskList,taskImg
    taskList=[61,87,2,4,6,8,10,11,12,13,15,18,23,24,27,30,32,36,37,39,40,42,46,48,49,50,52,53,54,76,80,81]
    taskImg = {_:0 for _ in taskList}

    for renwuid in taskList:
        taskImg[renwuid] = cv2.imread("./fonts/{}.png".format(renwuid))
        taskImg[renwuid] = cv2.cvtColor(taskImg[renwuid], cv2.COLOR_BGR2GRAY)
        ret, taskImg[renwuid] = cv2.threshold(taskImg[renwuid], 200, 255,cv2.THRESH_BINARY)
def getTaskId():
    renwu_mn = 1000000000
    renwu_mnid = 0
    renwu_menu_img = ImageGrab.grab((windowTopLeft[0]+48,windowTopLeft[1]+145,windowTopLeft[0]+48+220,windowTopLeft[1]+145+40))
    renwu_menu_img = cv2.cvtColor(numpy.array(renwu_menu_img), cv2.COLOR_RGB2BGR)
    renwu_menu_img = cv2.cvtColor(renwu_menu_img, cv2.COLOR_BGR2GRAY)
    ret, renwu_menu_img = cv2.threshold(renwu_menu_img, 200, 255,cv2.THRESH_BINARY)
    for renwuid in taskList:
        result = cv2.matchTemplate(renwu_menu_img,taskImg[renwuid],cv2.TM_SQDIFF)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        print(min_val,renwuid)
        if min_val<renwu_mn:
            renwu_mnid=renwuid
            renwu_mn=min_val
    return renwu_mnid
def checkTaskIsDone():
    gameimg = ImageGrab.grab((windowTopLeft[0]+896,windowTopLeft[1]+15,windowTopLeft[0]+1155,windowTopLeft[1]+229))
    gameimg = cv2.cvtColor(numpy.array(gameimg), cv2.COLOR_RGB2BGR)
    ximg = cv2.imread("./img/x.png")
    result = cv2.matchTemplate(gameimg,ximg,cv2.TM_SQDIFF)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    #print(min_val)
    return min_val<5930909
def ColourDistance(rgb_1, rgb_2):
    R_1,G_1,B_1 = rgb_1
    R_2,G_2,B_2 = rgb_2
    rmean = (R_1 +R_2 ) / 2
    R = R_1 - R_2
    G = G_1 -G_2
    B = B_1 - B_2
    return math.sqrt((2+rmean/256)*(R**2)+4*(G**2)+(2+(255-rmean)/256)*(B**2))
def testPix(screenshot,pos):
    pix = screenshot.getpixel((pos[0]+windowTopLeft[0], pos[1]+windowTopLeft[1]))
    return ColourDistance((230,149,31),pix)<=200
def correctTaskId(id):
    #同任务多点，靠完整地图判断
    pyautogui.click(windowTopLeft[0]+107,windowTopLeft[1]+167)
    time.sleep(0.1)
    press('tab')
    time.sleep(0.1)
    screenshot = pyautogui.screenshot()
    press('tab')
    time.sleep(0.1)
    if id == 12: #掸灰
        return (82 if testPix(screenshot,(518,240)) else (84 if testPix(screenshot,(667,240)) else (88 if testPix(screenshot,(521, 135)) else (12 if testPix(screenshot,(706,137)) else 69))))  
    if id == 4: #修建植物
        return (4 if testPix(screenshot,(477,147)) else 20)
    if id == 11: #点蜡烛
        return (83 if testPix(screenshot,(845,326)) else 11)
    if id==27: #签名
        return (86 if testPix(screenshot,(832,617)) else 27)
    if id==81:
        return (93 if testPix(screenshot,(729, 413)) else 81)
    if id==32: #拼图
        return (5 if testPix(screenshot,(521,137)) else (89 if testPix(screenshot,(518, 239)) else (91 if testPix(screenshot,(566, 580)) else (111 if testPix(screenshot,(706,137)) else 32))))

#键盘模拟相关
keyRev={'w':'s','a':'d','s':'w','d':'a'}
keyState={'w':0,'a':0,'s':0,'d':0}
def setKey(key,target):
    global keyState
    if(keyState[key]==target):
        return
    if(target==1):
        if(keyState[keyRev[key]]==1):
            up(keyRev[key])
            keyState[keyRev[key]]=0
        down(key)
    else:
        up(key)
    keyState[key]=target
def releaseAllKeys():
    setKey('s',0)
    setKey('w',0)
    setKey('a',0)
    setKey('d',0)
def moveGooseTo(pos):
    global keyState
    keyState={'w':0,'a':0,'s':0,'d':0}
    lastPos=(0,0)
    while True:
        curPos = getMyPos()
        if(curPos == -1):
            return -1
        print(curPos,pos,keyState)
        if(curPos==lastPos):
            print("stuck")
            rfx = random.choice(['w','a','s','d'])
            setKey(rfx,1)
            time.sleep(random.choice([0.3,0.6,0.2,0.4]))
            setKey(rfx,0)
            continue

        if(abs(curPos[0]-pos[0])<=2):
            setKey('d',0)
            setKey('a',0)
        else:
            if(curPos[0]<pos[0]):
                setKey('d',1)
            else:
                setKey('a',1)

        if(abs(curPos[1]-pos[1])<=2):
            setKey('s',0)
            setKey('w',0)
        else:
            if(curPos[1]<pos[1]):
                setKey('s',1)
            else:
                setKey('w',1)

        if((abs(curPos[1]-pos[1])<=2) and (abs(curPos[0]-pos[0])<=2)):
            releaseAllKeys()
            return 0
        lastPos=curPos
        #time.sleep(0.05)  
def randomMove():
    rfx = random.choice(['w','a','s','d'])
    down(rfx)
    time.sleep(random.choice([0.3,0.1,0.2,0.4]))
    up(rfx)
#游戏地图相关
def mapInit():
    global pointNum,edgeNum,x,y,pth
    f=open('map.txt','r+')
    pointNum,edgeNum=f.readline().split(' ')
    pointNum=int(pointNum)
    edgeNum=int(edgeNum)
    x=[0 for i in range(pointNum*2)]
    y=[0 for i in range(pointNum*2)]
    pth=[[] for i in range(pointNum*2)]
    for i in range(pointNum):
        line = f.readline()
        if(line == ""):
            break
        ord1 = list(map(lambda x:int(x),line.split(' ')))
        pid=ord1[0]
        x[pid]=ord1[1]
        y[pid]=ord1[2]
        
    for i in range(edgeNum):
        line = f.readline()
        if(line == ""):
            break
        ord1 = list(map(lambda x:int(x),line.split(' ')))
        p1=ord1[0]
        p2=ord1[1]
        pth[p1].append(p2)
        pth[p2].append(p1)
def findPath(s,t):
    res=[]
    Q=Queue(maxsize=0)
    Q.put(s)
    vis=[False for i in range(pointNum*2)]
    vis[s]=True
    bak=[0 for i in range(pointNum*2)]
    while(not Q.empty()):
        cur = Q.get()
        if(cur==t):
            break
        for nxt in pth[cur]:
            if(vis[nxt]==False):
                Q.put(nxt)
                vis[nxt]=True
                bak[nxt]=cur
    cur = t
    while (cur != 0):
        res.append(cur)
        cur=bak[cur]
    res.reverse()
    return res
def getClosetPoint(pos):
    def sqr(x):
        return x*x
    pid=0
    mn=1000000
    for i in range(pointNum*2):
        dis = sqr(pos[0]-x[i])+sqr(pos[1]-y[i])
        if(dis<mn):
            mn=dis
            pid=i
    return pid
def moveToTask(id):
    curPos = getMyPos()
    if(type(curPos) == int):
        return curPos
    
    S = getClosetPoint(curPos)
    #print(S)

    full_path = findPath(S,id)
    #print(full_path)
    for point in full_path:
        print('going to',point)
        if moveGooseTo((x[point],y[point]))==-1:
            return -1

#鼠标模拟相关
def moveTo(x,y,duration=0.25):
    pyautogui.moveTo(windowTopLeft[0]+x, windowTopLeft[1]+y, duration=duration)

#任务模拟相关
def cleanDust():    
    global currentTaskId
    if cleanOrPuzzle()==0:
        if(currentTaskId == 82):
            puzzle89()
        if(currentTaskId == 84):
            puzzle32()
        if(currentTaskId == 88):
            puzzle1()
        if(currentTaskId == 12):
            puzzle5()
        return
    moveTo(675, 358, duration=0.25)
    for _ in range(10):
        pyautogui.click()
        time.sleep(0.25)
def lightCandle():
    moveTo(911, 207)
    pyautogui.mouseDown()
    moveTo(779, 298)
    time.sleep(1)
    pyautogui.mouseUp()
    moveTo(779, 298)
    pyautogui.mouseDown()
    moveTo(652, 293)
    time.sleep(1)
    pyautogui.mouseUp()
    moveTo(651, 293)
    pyautogui.mouseDown()
    moveTo(514, 290)
    time.sleep(1)
    pyautogui.mouseUp()
def prunePlant():
    moveTo(696, 524)
    pyautogui.mouseDown()
    t=0.4
    moveTo(871, 364, duration = t)
    moveTo(852, 315, duration = t)
    moveTo(782, 252, duration = t)
    moveTo(776, 248, duration = t)
    moveTo(705, 226, duration = t)
    moveTo(689, 219, duration = t)
    moveTo(682, 222, duration = t)
    moveTo(639, 229, duration = t)
    moveTo(565, 248, duration = t)
    moveTo(530, 260, duration = t)
    moveTo(490, 280, duration = t)
    moveTo(475, 321, duration = t)
    moveTo(466, 403, duration = t)
    moveTo(445, 405, duration = t)
    moveTo(450, 384, duration = t)
    pyautogui.mouseUp()

def cleanOrPuzzle():
    #因为拼图和掸灰位置重复，在这里重新判断任务
    moveTo(658, 370)
    gameimg = ImageGrab.grab((windowTopLeft[0]+404,windowTopLeft[1]+155,windowTopLeft[0]+866,windowTopLeft[1]+635))
    gameimg = cv2.cvtColor(numpy.array(gameimg), cv2.COLOR_RGB2BGR)
    mimg = cv2.imread("./img/m.png")
    result = cv2.matchTemplate(gameimg,mimg,cv2.TM_SQDIFF)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    if min_val<1000000:
        return 1
    return 0
def puzzle32():
    if cleanOrPuzzle():
        cleanDust()
        return
    moveTo(376, 197)
    pyautogui.mouseDown()
    moveTo(709, 280)
    pyautogui.mouseUp()
    moveTo(901, 242)
    pyautogui.mouseDown()
    moveTo(673, 451)
    pyautogui.mouseUp()
    moveTo(891, 470)
    pyautogui.mouseDown()
    moveTo(574, 326)
    pyautogui.mouseUp()
    moveTo(358, 339)
    pyautogui.mouseDown()
    moveTo(665, 521)
    pyautogui.mouseUp()
    moveTo(348, 536)
    pyautogui.mouseDown()
    moveTo(541, 449)
    pyautogui.mouseUp()
def puzzle1():
    if cleanOrPuzzle():
        cleanDust()
        return
    moveTo(369, 215)
    pyautogui.mouseDown()
    moveTo(658, 350)
    pyautogui.mouseUp()
    moveTo(916, 173)
    pyautogui.mouseDown()
    moveTo(643, 344)
    pyautogui.mouseUp()
    moveTo(937, 454)
    pyautogui.mouseDown()
    moveTo(544, 442)
    pyautogui.mouseUp()
    moveTo(344, 517)
    pyautogui.mouseDown()
    moveTo(715, 424)
    pyautogui.mouseUp()
    moveTo(955, 637)
    pyautogui.mouseDown()
    moveTo(658, 511)
    pyautogui.mouseUp()
def puzzle89():
    if cleanOrPuzzle():
        cleanDust()
        return
    moveTo(339, 210)
    pyautogui.mouseDown()
    moveTo(603, 313)
    pyautogui.mouseUp()
    moveTo(877, 275)
    pyautogui.mouseDown()
    moveTo(597, 461)
    pyautogui.mouseUp()
    moveTo(367, 492)
    pyautogui.mouseDown()
    moveTo(644, 457)
    pyautogui.mouseUp()
    moveTo(915, 489)
    pyautogui.mouseDown()
    moveTo(694, 348)
    pyautogui.mouseUp()
def puzzle5():
    if cleanOrPuzzle():
        cleanDust()
        return
    moveTo(342, 196)
    pyautogui.mouseDown()

    moveTo(588, 295)
    pyautogui.mouseUp()

    moveTo(318, 424)
    pyautogui.mouseDown()

    moveTo(567, 418)
    pyautogui.mouseUp()

    moveTo(882, 216)
    pyautogui.mouseDown()

    moveTo(679, 457)
    pyautogui.mouseUp()

    moveTo(928, 414)
    pyautogui.mouseDown()

    moveTo(695, 304)
    pyautogui.mouseUp()

    moveTo(944, 605)
    pyautogui.mouseDown()

    moveTo(577, 498)
    pyautogui.mouseUp()
def puzzle91():
    if cleanOrPuzzle():
        cleanDust()
        return
    moveTo(348, 171)
    pyautogui.mouseDown()
    moveTo(607, 305)
    pyautogui.mouseUp()
    moveTo(921, 280)
    pyautogui.mouseDown()
    moveTo(591, 445)
    pyautogui.mouseUp()
    moveTo(395, 400)
    pyautogui.mouseDown()
    moveTo(686, 337)
    pyautogui.mouseUp()
    moveTo(942, 495)
    pyautogui.mouseDown()
    moveTo(698, 461)
    pyautogui.mouseUp()
    moveTo(326, 621)
    pyautogui.mouseDown()
    moveTo(567, 515)
    pyautogui.mouseUp()
def coalTransport():
    for _ in range(5):
        moveTo(644, 392)
        pyautogui.mouseDown()

        moveTo(644, 392)
        pyautogui.mouseUp()

        moveTo(841, 554)
        pyautogui.mouseDown()

        moveTo(841, 554)
        pyautogui.mouseUp()
def findQueen():
    pyautogui.click(windowTopLeft[0]+424, windowTopLeft[1]+359)
    pyautogui.click(windowTopLeft[0]+634, windowTopLeft[1]+357)
    pyautogui.click(windowTopLeft[0]+861, windowTopLeft[1]+356)
    time.sleep(13)
    pyautogui.click(windowTopLeft[0]+424, windowTopLeft[1]+359)
    time.sleep(2)
def cleanTank():
    moveTo(346, 395)
    pyautogui.mouseDown()
    t=0.2
    for _ in range(6):
        moveTo(444, 219,duration=t)
        moveTo(775, 218,duration=t)
    for _ in range(10):
        moveTo(444, 334,duration=t)
        moveTo(775, 342,duration=t)
    for _ in range(6):
        moveTo(444, 448,duration=t)
        moveTo(775, 460,duration=t)
    for _ in range(12):
        moveTo(484, 554,duration=t)
        moveTo(825, 570,duration=t)
    pyautogui.mouseUp()
def cleanStatue():
    moveTo(346, 395)
    pyautogui.mouseDown()
    t=0.2
    for _ in range(6):
        moveTo(444, 219,duration=t)
        moveTo(775, 218,duration=t)
    for _ in range(10):
        moveTo(444, 428,duration=t)
        moveTo(835, 440,duration=t)
    pyautogui.mouseUp()
def pokeBody():
    moveTo(876, 354)
    pyautogui.mouseDown()
    for _ in range(3):
        moveTo(698, 534)
        moveTo(876, 354)
    pyautogui.mouseUp()
def fishing():
    while True:
        pix = pyautogui.screenshot().getpixel((611+windowTopLeft[0], 471+windowTopLeft[1]))
        if(pix[0]<=240):
            time.sleep(0.2)
            moveTo(673, 213)
            pyautogui.click()
            break
def sign():
    moveTo(765, 440)
    pyautogui.click()
def catchMouse():
    moveTo(990, 177)
    mouseimg = cv2.imread("./img/Mouse.png")
    gg = 0 
    while gg<=4:
        gameimage = ImageGrab.grab((*windowTopLeft,*windowLowerRight))
        gameimage = cv2.cvtColor(numpy.array(gameimage), cv2.COLOR_RGB2BGR)
        theight, twidth = mouseimg.shape[:2]
        result = cv2.matchTemplate(gameimage,mouseimg,cv2.TM_SQDIFF)
        #cv2.normalize( result, result, 0, 1, cv2.NORM_MINMAX, -1 )
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        if(min_val<5000000):
            #print(min_val)
            gg+=1
            x=min_loc[0]+twidth//2
            y=min_loc[1]+theight//2
            pyautogui.click(x+windowTopLeft[0],y+windowTopLeft[1])
            moveTo(990, 177,duration=0)
def flavoring():
    t=0.1
    moveTo(805, 220)
    pyautogui.mouseDown()
    for _ in range(8):
        moveTo(812, 314, duration=t)
        moveTo(805, 220, duration=t)
    pyautogui.mouseUp()

    moveTo(492, 222)
    pyautogui.mouseDown()
    for _ in range(8):
        moveTo(483, 326, duration=t)
        moveTo(492, 222, duration=t)
    pyautogui.mouseUp()
def openStatue():
    moveTo(667, 386)
    pyautogui.click()
def getCloth():
    moveTo(604, 402)
    pyautogui.mouseDown()
    moveTo(883, 550)
    pyautogui.mouseUp()
def putCloth():
    moveTo(790, 352)
    pyautogui.mouseDown()
    moveTo(790, 351)
    pyautogui.mouseUp()
    moveTo(955, 556)
    pyautogui.mouseDown()
    moveTo(630, 380)
    pyautogui.mouseUp()
def sweepFloor():
    moveTo(824, 296)
    pyautogui.mouseDown()
    moveTo(730, 491)
    pyautogui.mouseUp()
    moveTo(724, 488)
    pyautogui.mouseDown()
    moveTo(735, 106)
    pyautogui.mouseUp()
    moveTo(725, 103)
    pyautogui.mouseDown()
    moveTo(734, 506)
    pyautogui.mouseUp()
    moveTo(726, 504)
    pyautogui.mouseDown()
    moveTo(635, 510)
    pyautogui.mouseUp()
    moveTo(627, 509)
    pyautogui.mouseDown()
    moveTo(653, 121)
    pyautogui.mouseUp()
    moveTo(646, 119)
    pyautogui.mouseDown()
    moveTo(642, 499)
    pyautogui.mouseUp()
    moveTo(637, 499)
    pyautogui.mouseDown()
    moveTo(508, 504)
    pyautogui.mouseUp()
    moveTo(503, 501)
    pyautogui.mouseDown()
    moveTo(593, 110)
    pyautogui.mouseUp()
def cleanLight():
    moveTo(357, 393)
    pyautogui.mouseDown()
    for _ in range(10):
        moveTo(334, 546)
        moveTo(624, 417)
    for _ in range(10):
        moveTo(731, 483)
        moveTo(889, 605)
    for _ in range(9):
        moveTo(702, 293)
        moveTo(703, 149)
    pyautogui.mouseUp()
def sweepFloor2():
    moveTo(900, 298)
    pyautogui.mouseDown()
    moveTo(637, 132)
    time.sleep(1.5)
    moveTo(745, 280)
    time.sleep(1.5)
    moveTo(695, 456)
    time.sleep(1.5)
    moveTo(505, 358)
    time.sleep(1.5)
    pyautogui.mouseUp()
def clearBB():
    moveTo(654, 388)
    pyautogui.mouseDown()
    for _ in range(14):
        moveTo(401, 298)
        moveTo(854, 299)
    pyautogui.mouseUp()
def chemistry():
    tps=[[495,490],[623,490],[752,490]]
    optionsimage = ImageGrab.grab((windowTopLeft[0]+375,windowTopLeft[1]+539,windowTopLeft[0]+910,windowTopLeft[1]+577))
    optionsimage = cv2.cvtColor(numpy.array(optionsimage), cv2.COLOR_RGB2BGR)
    for tp in tps:
        gameimage = ImageGrab.grab((windowTopLeft[0]+tp[0],windowTopLeft[1]+tp[1],windowTopLeft[0]+tp[0]+35,windowTopLeft[1]+tp[1]+18))
        gameimage = cv2.cvtColor(numpy.array(gameimage), cv2.COLOR_RGB2BGR)
        theight, twidth = gameimage.shape[:2]
        result = cv2.matchTemplate(optionsimage,gameimage,cv2.TM_SQDIFF)
        #cv2.normalize( result, result, 0, 1, cv2.NORM_MINMAX, -1 )
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        x=375+min_loc[0]+twidth//2
        y=539+min_loc[1]+theight//2
        pyautogui.click(x+windowTopLeft[0],y+windowTopLeft[1])
        time.sleep(0.5)
def pipe():
    def isred(pix):
        return (120<=pix[0]<=135)and(34<=pix[1]<=37)and(32<=pix[2]<=40)
    img = pyautogui.screenshot()
    target = [0,1,0,0]
    poss=[[548,224],[548,389],[815,339],[885,457]]
    clickposs=[[548,168],[550,452],[814,277],[823,458]]
    for _ in range(4):
        pix = img.getpixel((poss[_][0]+windowTopLeft[0], poss[_][1]+windowTopLeft[1])) 
        #print(_,pix,isred(pix))
        if(isred(pix) != target[_]):
            #pass
            pyautogui.click(clickposs[_][0]+windowTopLeft[0], clickposs[_][1]+windowTopLeft[1])
def cleanArmor():
    moveTo(928, 151)
    pyautogui.mouseDown()
    for _ in range(6):
        moveTo(833, 333)
        moveTo(450, 350)
    for _ in range(6):
        moveTo(308, 611,duration=0.4)
        moveTo(980, 609,duration=0.4)
    pyautogui.mouseUp()
def unlock():
    moveTo(829, 330)
    pyautogui.mouseDown()
    for _ in range(5):
        moveTo(720, 400,duration=0.1)
        moveTo(709, 672,duration=0.1)
    pyautogui.mouseUp()
def getBook():
    moveTo(315, 218)
    pyautogui.mouseDown()
    moveTo(166, 273)
    pyautogui.mouseUp()
    moveTo(545, 383)
    pyautogui.mouseDown()
    moveTo(166, 273)
    pyautogui.mouseUp()
    moveTo(687, 515)
    pyautogui.mouseDown()
    moveTo(166, 273)
    pyautogui.mouseUp()
def lightCandle2():
    moveTo(930, 242)
    pyautogui.mouseDown()
    moveTo(590, 278)
    time.sleep(1)
    pyautogui.mouseUp()
def openBox():
    moveTo(394, 369)
    pyautogui.mouseDown()
    moveTo(716, 547)
    pyautogui.mouseUp()
    moveTo(716, 547)
    pyautogui.mouseDown()
    moveTo(662, 154)
    pyautogui.mouseUp()
def putBook():
    moveTo(306, 213)
    pyautogui.mouseDown()
    moveTo(300, 532)
    moveTo(1012, 534,duration=2)
    pyautogui.mouseUp()

    moveTo(300, 357)
    pyautogui.mouseDown()
    moveTo(1007, 361,duration=2)
    pyautogui.mouseUp()

    moveTo(306, 491)
    pyautogui.mouseDown()
    moveTo(314, 180)
    moveTo(1000, 180,duration=2)
    pyautogui.mouseUp()
def organizingBox():
    sign={}
    pos={}
    sign[1]=cv2.imread("./img/1.png")
    sign[2]=cv2.imread("./img/2.png")
    sign[10]=cv2.imread("./img/10.png")
    sign[20]=cv2.imread("./img/20.png")
    sign[30]=cv2.imread("./img/30.png")
    initpos={
        11:(366, 588),
        21:(371, 504),
        31:(467, 586),
        12:(976, 597),
        22:(473, 498),
        32:(878, 599)
    }
    gameimage = ImageGrab.grab((windowTopLeft[0]+248,windowTopLeft[1]+103,windowTopLeft[0]+248+794,windowTopLeft[1]+103+357))
    gameimage = cv2.cvtColor(numpy.array(gameimage), cv2.COLOR_RGB2BGR)
    for signbit in [1,2,10,20,30]:
        theight, twidth = sign[signbit].shape[:2]
        result = cv2.matchTemplate(gameimage,sign[signbit],cv2.TM_SQDIFF)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        pos[signbit]=(min_loc[0]+28+248,min_loc[1]+28+103+30)
    for s1 in [1,2]:
        for s2 in [10,20,30]:
            pos[s2+s1]=(pos[s2][0],pos[s1][1])
            moveTo(*initpos[s1+s2])
            pyautogui.mouseDown()
            moveTo(*pos[s2+s1])
            pyautogui.mouseUp()
def planets():
    initx=[352,509,705,882]
    tryy=[575,585,595,606,613]
    finals=[(342, 217),(510, 228),(508, 326),(636, 296),(900, 275),(730, 362),(782, 336),(796, 218),(415, 315)]
    for x in initx:
        for y in tryy:
            moveTo(x, y,duration=0)
            pyautogui.mouseDown()
            moveTo(x,560,duration=0.1)
            pyautogui.mouseUp()
        pyautogui.mouseDown()
        for final in finals:
            moveTo(*final,duration=0.1)
        pyautogui.mouseUp()
def flask():
    options=[(343, 573),(464, 571),(573, 569),(692, 578),(800, 570),(907, 569)]
    bias = (146,36)
    allimage = ImageGrab.grab((windowTopLeft[0]+294,windowTopLeft[1]+99,windowTopLeft[0]+992,windowTopLeft[1]+434))
    allimage = cv2.cvtColor(numpy.array(allimage), cv2.COLOR_RGB2BGR)
    for tp in options:
        gameimage = ImageGrab.grab((windowTopLeft[0]+tp[0],windowTopLeft[1]+tp[1],windowTopLeft[0]+tp[0]+28,windowTopLeft[1]+tp[1]+28))
        gameimage = cv2.cvtColor(numpy.array(gameimage), cv2.COLOR_RGB2BGR)
        gameimage = cv2.resize(gameimage, (46, 46), interpolation=cv2.INTER_CUBIC)
        theight, twidth = gameimage.shape[:2]
        result = cv2.matchTemplate(allimage,gameimage,cv2.TM_SQDIFF)
        #cv2.normalize( result, result, 0, 1, cv2.NORM_MINMAX, -1 )
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        x=294+min_loc[0]+twidth//2
        y=99+min_loc[1]+theight//2
        if (x<=640):
            x+=bias[0]
        else:
            x-=bias[0]
        y+=bias[1]
        moveTo(tp[0], tp[1])
        pyautogui.mouseDown()
        moveTo(x, y)
        pyautogui.mouseUp()
        time.sleep(0.1)
def Oscilloscope():
    def get_first_color(color):
        for i in range(392,550):
            pix = gameimage.getpixel((i, 382))
            if(pix==color):
                return i
        return -1
    def move_ss(color):
        blue_pos=get_first_color(color)
        if(blue_pos==-1):
            return
        print(blue_pos)
        white_pos=443
        if(blue_pos>white_pos):
            fx=-1
        else:
            fx=1
        rounds=abs(blue_pos-white_pos)//2
        moveTo(*poss[0])
        pyautogui.mouseDown()
        cur=0
        for i in range(rounds):
            cur=(cur+fx + 4) % 4;
            moveTo(*poss[cur],duration=0.15)
        pyautogui.mouseUp()
    for tt in range(3):
        poss=[(562, 536),(523, 575),(563, 611),(601, 577)]
        gameimage = ImageGrab.grab((*windowTopLeft,*windowLowerRight))
        move_ss((0,0,255))
        poss=[(_[0]+154,_[1]) for _ in poss]
        gameimage = ImageGrab.grab((*windowTopLeft,*windowLowerRight))
        move_ss((255,0,0))
def putFlower():
    moveTo(919, 460)
    pyautogui.mouseDown()
    moveTo(684, 397)
    pyautogui.mouseUp()
id2func={
        87:cleanArmor,
        2:unlock,
        4:prunePlant,
        20:prunePlant,
        6:cleanTank,
        8:chemistry,
        10:flask,
        11:lightCandle,
        83:lightCandle2,
        12:cleanDust,
        82:cleanDust,
        69:cleanDust,
        88:cleanDust,
        13:findQueen,
        15:Oscilloscope,
        18:coalTransport,
        23:pokeBody,
        24:fishing,
        27:sign,
        86:sign,
        30:getBook,
        32:puzzle32,
        5:puzzle1,
        89:puzzle89,
        91:puzzle91,
        111:puzzle5,
        84:cleanDust,
        36:flavoring,
        37:catchMouse,
        39:sweepFloor,
        40:cleanLight,
        42:sweepFloor2,
        46:planets,
        48:clearBB,
        49:getCloth,
        50:putCloth,
        52:cleanStatue,
        53:organizingBox,
        54:openStatue,
        76:openBox,
        80:pipe,
        81:putBook,
        93:putBook,
        61:putFlower
    }

#状态检测
def testPixAll(x,y,target):
    pix = pyautogui.screenshot().getpixel((x+windowTopLeft[0], y+windowTopLeft[1]))
    print(pix)
    return pix == target
def isInLobby():
    return testPixAll(1187,541,(255,255,255))
def isReady():
    return testPixAll(634,639,(165,198,49))
def isInGame():
    return testPixAll(1201,177,(217,205,181))
def getRole():
    #0=goose 1=duck
    if(testPixAll(472, 82,(255,255,255))):
        return 0
    if(testPixAll(472, 82,(255,0,0))):
        return 1
    return 2
def isAllReady():
    return testPixAll(706, 654,(115,115,115))

def mainLoop():
    global currentTaskId
    while 1:
        currentTaskId = getTaskId()
        if(currentTaskId in [4,11,12,27,32,81]):
            currentTaskId = correctTaskId(currentTaskId)
        print('当前任务',currentTaskId)
        res = moveToTask(currentTaskId)
        if(res == -1):
            return
        if(res == -2):
            continue
        press('e')
        print('进入任务',currentTaskId)
        time.sleep(1)
        retryTime = 0
        failTime = 0
        while(checkTaskIsDone()):
            print('任务未完成',currentTaskId)
            retryTime+=1
            failTime+=1
            if retryTime == 3:
                retryTime=0
                press('esc')
                time.sleep(1)
                press('e')
                time.sleep(1)
            if failTime == 8:
                press('esc')
                time.sleep(1)
                break
            id2func[currentTaskId]()
            time.sleep(2)

mapInit()
screenShotInit()
taskTextInit()
time.sleep(1)
mainLoop()
while 1:
    while(not isInLobby()):
        time.sleep(1)
    print('进入大厅')
    if isHost:
        while(isAllReady()):
            time.sleep(1)
        pyautogui.click(706+windowTopLeft[0], 654+windowTopLeft[1])
        time.sleep(0.5)
    else:
        while(not isReady()):
            moveTo(700,641,duration=0)
            pyautogui.click()
            time.sleep(0.5)
    print('已准备')
    while(not isInGame()):
        if(not isHost):
            if(not isReady()):
                moveTo(700,641,duration=0)
                pyautogui.click()
                #time.sleep(0.5)
        time.sleep(0.5)
    role = getRole()
    print('进入游戏 角色',role)
    releaseAllKeys()
    if(role == 0):
        mainLoop()
    else:
        while(not isInLobby()):
            randomMove()
