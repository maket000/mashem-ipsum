from random import random, randint, normalvariate

BASESTARTROW = 2
STARTROWVARIATION = 1

NORMALIZEFACTORW = 0.3
NORMALIZEFACTORH = 0.3
NEUTRALPULLFACTOR = 0.4

MOVESIGW = 0.5
MOVESIGH = 0.5

DOUBLEPUSH = 0.1

def readMapFile(filename):
    layouts = {}
    fileobj = open(filename)
    layoutname = False
    for line in fileobj.readlines():
        line = line.strip()
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
    
    startingrow = normalvariate(BASESTARTROW, STARTROWVARIATION)
    startingcolL = 1 #+ random()
    startingcolR = 7 #6 + 2*random()

    fingers = [[[startingcolL+i, startingrow] for i in range(4)],
               [[startingcolR+i, startingrow] for i in range(4)]]
    cooldown = [1 for c in range(8)]
    hotness = 8

    string = ""
    for c in range(length):
        choice = randint(1,hotness)
        for f in range(len(cooldown)):
            if choice <= cooldown[f]:
                fingers[f//4][f%4] = pressMove(fingers[f//4][f%4])
                string += posToKey(layout, fingers[f//4][f%4], False)
                
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

    return string
        
layouts = readMapFile("keymaps.cfg")

print("Mash Generator")
print("Supported layouts: %s" % (", ".join(layouts.keys())))
print("Type 'quit' to exit\n")

while 1:
    layout = input("mash layout: ")
    if layout == "quit":
        break
    while layout not in layouts:
        print("Unsupported layout.")
        layout = input("mash layout: ")
        if layout == "quit":
            break

    length = input("mash length: ")
    if length == "quit":
        break
    while not length.isdigit():
        print("Invalid length.")
        length = input("mash length: ")
        if length == "quit":
            break
    print("%s\n" % (standardMash(layout, int(length))))
