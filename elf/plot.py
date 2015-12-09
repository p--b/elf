class Plot:
    def __init__(self, itemClass, act):
        self.act         = act
        self.itemClass   = itemClass
        self.cardinality = itemClass.cardinality
        self.targetSize  = act.size()
        self.scenes      = []

    def addNextScene():
        if len(self.scenes) >= self.targetSize:
            raise RuntimeError('Cannot expand plot past target size!')

        if len(self.scenes):
            self.scenes.append(PlotScene(self,
                                         self.scenes[-1].scene.next(),
                                         self.scenes[-1]))
        else:
            self.scenes.append(PlotScene(self,
                                         self.act.firstScene(),
                                         None))

        return self.scenes[-1]

class PlotScene:
    def __init__(self, plot, scene, previous):
        self.plot     = plot
        self.scene    = scene
        self.previous = previous
        self.next     = None
        self.pickups  = [None] * plot.cardinality

        if self.previous != None:
            self.previous.next = self

    def pickup(self, itemId, owner):
        if self.pickups[itemId] != None:
            raise RuntimeException("Item already picked up!")

        self.pickups[itemId] = owner

    def whoHas(self, itemId):
        target = self

        while True:
            if target.pickups[itemId] != None:
                return target.pickups[itemId]

            if target.previous == None:
                return None
            else:
                target = target.previous

    def currentlyHeldBy(self, owner):
        index = self.heldWhichLast(owner)

        if index == None:
            return None

        if owner == self.whoHas(index):
            return index

        return None

    def heldWhichLast(self, owner):
        target = self

        while True:
            try:
                return target.pickups.index(owner)

            except ValueError:
                if target.previous == None:
                    return None
                else:
                    target = target.previous
