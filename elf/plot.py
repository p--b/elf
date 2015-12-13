class Plot:
    def __init__(self, itemClass, act):
        self.act         = act
        self.itemClass   = itemClass
        self.cardinality = itemClass.cardinality
        self.targetSize  = act.size()
        self.scenes      = []

    def __len__(self):
        return len(self.scenes)

    def addNextScene(self):
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

    def getUtilisation(self):
        pickupIndexSet = set()

        for scene in self.scenes:
            for index, actor in scene.getPickups().iteritems():
                pickupIndexSet.add(index)

        return len(pickupIndexSet)

    def getActorItems(self):
        actItems = {}

        for scene in self.scenes:
            for item, actor in scene.getPickups().iteritems():
                if actor not in actItems:
                    actItems[actor] = set()

                actItems[actor].add(item)

        return actItems

    def getItemActors(self):
        itemActors = {}

        for scene in self.scenes:
            for item, actor in scene.getPickups().iteritems():
                if item not in itemActors:
                    itemActors[item] = set()

                itemActors[item].add(actor)

        return itemActors

    def __str__(self):
        scenes = ''

        for scene in self.scenes:
            scenes += str(scene) + '\n'

        return "Plot [%i/%i]\n" % (len(self.scenes),
                                   self.targetSize) + scenes

class PlotScene:
    def __init__(self, plot, scene, previous):
        self.plot      = plot
        self.scene     = scene
        self.previous  = previous
        self.next      = None
        self.pickups   = [None] * plot.cardinality
        self.pickupSet = set()

        if self.previous != None:
            self.previous.next = self

    def getShowScene(self):
        return self.scene

    def pickup(self, itemId, owner):
        if self.pickups[itemId] != None:
            raise RuntimeException("Item already picked up!")

        self.pickups[itemId] = owner
        self.pickupSet.add(owner)

    def getPickups(self):
        return {item: actor for item, actor in enumerate(self.pickups) \
                            if actor != None}

    def __len__(self):
        return len(self.pickupSet)

    def distanceToUse(self, itemId):
        actor     = self.whoHas(itemId)
        showScene = self.scene
        distance  = 0

        while None != showScene:
            if showScene.hasActor(actor):
                return distance

            distance += 1
            showScene = showScene.next()
        else:
            return -1

        return distance

    def pickupInScene(self, owner):
        return owner in self.pickupSet

    def whoHas(self, itemId):
        target = self

        while True:
            if target.pickups[itemId] != None:
                return target.pickups[itemId]

            if target.previous == None:
                return None
            else:
                target = target.previous

    def getUnused(self):
        unused = set()

        for item in range(self.plot.cardinality):
            if None == self.whoHas(item):
                unused.add(item)

        return unused

    def getAvailable(self):
        # TODO: Return items held by actors that never need
        #       an item again
        pass

    def getStrictlyAvailable(self):
        # TODO: Return items held by actors that do not need
        #       an item in this scene
        pass

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

    def __str__(self):
        return 'Scene[%s:%s]: %s' % (self.scene.id,
                                     self.scene.name,
                                     self.getPickups())
