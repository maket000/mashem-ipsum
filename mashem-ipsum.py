from random import random, randint, normalvariate

NORMALIZEFACTORW = 0.2
NORMALIZEFACTORH = 0.2
NEUTRALPULLFACTOR = 0.1
MINSPACE = 0.6

MOVESIGW = 0.8
MOVESIGH = 0.8

DOUBLEPUSH = 0.1

def readMapFile(filename):
    layouts = {}
    fileobj = open(filename)
    layoutname = False
    for line in fileobj.readlines():
        line = line.rstrip()
        if line[0] == '~':
            if layoutname:
                layouts[layoutname] = layout
            spline = line.split('~')
            layoutname = spline[1]
            line = '~'.join(spline[2:])
            row = -1
            layout = {}
        keys = line.split(' ')
        for col,key in enumerate(keys):
            layout[(col,row)] = key
        row += 1            
    fileobj.close()
    layouts[layoutname] = layout
    return layouts


def posToKey(layout, pos, mod):
    """Returns a key(s) that would be pressed by a finger at pos, mod denotes
alternate key values"""

    nc = round(pos[0])
    nr = round(pos[1])
    mc = pos[0]-.5
    mr = pos[1]-.5
    mc = round(mc) - mc
    mr = round(mr) - mr
    amc = abs(mc)
    amr = abs(mr)
    press = ""
    try: press += layouts[layout][(nc,nr)][mod]
    except: pass
    if 0 < amc < DOUBLEPUSH:
        try: press += layouts[layout][(nc+mc/amc,nr)][mod]
        except: pass
        if 0 < amr < DOUBLEPUSH:
            try: press += layouts[layout][(nc+mc/amc,nr+mr/amr)][mod]
            except: pass
    if 0 < amr < DOUBLEPUSH:
        try: press += layouts[layout][(nc,nr+mr/amr)][mod]
        except: pass
    #print (pos, press)
    return press
        
    

def normalizeHand(hand):
    """Moves the fingers in a hand nearer to each other vertically, and equally
spaces them horizontally"""
    
    fingers = len(hand)
    sumW = 0
    sumH = 0
    spaceSum = 0
    for f in range(fingers):
        sumW += hand[f][0]
        sumH += hand[f][1]
        if f != fingers-1:
            spaceSum += hand[f+1][0] - hand[f][0]
    middle = sumW/fingers
    space = spaceSum/fingers
    if space < MINSPACE:
        space = MINSPACE
    left = middle - 2*space
    avgH = sumH/fingers
        
    for f in range(fingers):
        hand[f][0] += NORMALIZEFACTORW*((left+f*space) - hand[f][0])
        hand[f][1] += NORMALIZEFACTORH*(avgH-hand[f][1])

        
def pullToNeutral(hand, scol, srow):
    "Moves the positions in the hand back to the starting row and column"

    for f in range(len(hand)):
        hand[f][0] += NEUTRALPULLFACTOR*((scol+f) - hand[f][0])
        hand[f][1] += NEUTRALPULLFACTOR*(srow - hand[f][1])
    

def pressMove(position):
    "Gets a new position as if the finger was voraciously striking a nearby key"

    return [normalvariate(position[0],MOVESIGW),
            normalvariate(position[1],MOVESIGH)]
    

def standardMash(layout, length):
    """Mashes a length of characters as if it was done by someone typing very
neatly with random finger movement"""
    
    startingrow = 1.8
    startingcolL = 1 #+ random()
    startingcolR = 7 #6 + 2*random()

    fingers = [[[startingcolL+i, startingrow] for i in range(4)],
               [[startingcolR+i, startingrow] for i in range(4)]]
    cooldown = [1 for c in range(8)]
    hotness = 8

    mash = ""
    while len(mash) < length:
        choice = randint(1,hotness)
        for f in range(len(cooldown)):
            if choice <= cooldown[f]:
                fingers[f//4][f%4] = pressMove(fingers[f//4][f%4])
                hit = f

                choice = hotness + 1 #extra hot
                choice += 1 #TOO HOT
                choice -= 1 #whew
                hotness -= cooldown[f]
                cooldown[f] = 0
            choice -= cooldown[f]
            cooldown[f] += 1
        hotness += 8
        normalizeHand(fingers[0])
        normalizeHand(fingers[1])
        pullToNeutral(fingers[0], startingcolL, startingrow)
        pullToNeutral(fingers[1], startingcolR, startingrow)
        for m in posToKey(layout, fingers[hit//4][hit%4], False):
            if m not in banned:
                mash += m
    return mash[:length]


def getValidInput(condition, prompt, error):
    inp = input(prompt)
    while eval(condition):
        print(error)
        inp = input(prompt)
    return inp

        
layouts = readMapFile("keymaps.cfg")

print("Mash Generator")
print("Supported layouts: %s" % (", ".join(layouts.keys())))
banned = input("Please type all the characters you do not want in the mash: ")


layout = getValidInput("inp not in layouts","Mash layout: ",
                       "Unsupported layout.")
length = getValidInput("not inp.isdigit()", "Mash length: ", "Invalid length.")

print("%s" % (standardMash(layout, int(length))))
