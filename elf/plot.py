from copy import copy

class Plot(object):
    plotCounter = 0

    def __init__(self, itemClass, act):
        self.act         = act
        self.itemClass   = itemClass
        self.cardinality = itemClass.cardinality
        self.targetSize  = act.size()
        self.scenes      = []
        self.plotId      = Plot.plotCounter

        Plot.plotCounter += 1

    def __len__(self):
        return len(self.scenes)

    def addNextScene(self):
# FIXME: There appears to be a bug where duplicate plots make it into the candidates list. This causes
#        Them to be processed, and hence extended, twice...
        if len(self.scenes) >= self.targetSize:
#            raise RuntimeError('Cannot expand plot (size %d) past target size %d!' % (len(self.scenes), self.targetSize))
            return None

        if len(self.scenes):
            self.scenes.append(PlotScene(self,
                                         self.scenes[-1].scene.next(),
                                         self.scenes[-1]))
        else:
            self.scenes.append(PlotScene(self,
                                         self.act.firstScene(),
                                         None))

        return self.scenes[-1]

    def getSceneIndex(self, index):
        return self.scenes[index]

    def last(self):
        return self.getSceneIndex(-1)

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

    def cloneDiverge(self):
        clone        = copy(self)
        clone.scenes = copy(self.scenes)

        # Ensure the last scene is a new object
        clone.scenes[-1] = copy(clone.scenes[-1])
        clone.scenes[-1].plot = clone
        clone.plotId = Plot.plotCounter

        Plot.plotCounter += 1

        return clone

    def __str__(self):
        scenes = ''

        for scene in self.scenes:
            scenes += str(scene) + '\n'

        return "Plot<%i> [%i/%i]\n" % (self.plotId,
                                       len(self.scenes),
                                       self.targetSize) + scenes

class PlotScene(object):
    def __init__(self, plot, scene, previous):
        self.plot      = plot
        self.scene     = scene
        self.previous  = previous
        self.next      = None
        self.pickups   = [None] * plot.cardinality
        self.pickupSet = set()
        self.index     = 0

        if self.previous != None:
            self.previous.next = self
            self.index = self.previous.index + 1

    def __copy__(self):
        cls   = self.__class__
        clone = cls.__new__(cls)
        clone.__dict__.update(self.__dict__)

        clone.pickups = list(self.pickups)
        clone.pickupSet = set(self.pickupSet)

        return clone

    def getShowScene(self):
        return self.scene

    def pickup(self, itemId, owner):
        if self.pickups[itemId] != None:
            raise RuntimeError("[%d-%d]: Attempted pickup of <%d> by %s; already owned by %s" % (self.plot.plotId, self.index, itemId, owner, self.pickups[itemId]))

        # TODO: We should erase previous eager assignments.
        #       Note that it isn't this simple, as PlotScenes
        #       are shared between plots...!

        self.pickups[itemId] = owner
        self.pickupSet.add(owner)

        return self

    def getPickups(self):
        return {item: actor for item, actor in enumerate(self.pickups) \
                            if actor != None}

    def getCurrentAssignments(self):
        assignments = list(self.pickups)

        for item, actor in enumerate(assignments):
            if actor == None:
                assignments[item] = self.whoHas(item)

        return assignments

    def __len__(self):
        return len(self.pickupSet)

    def distanceToUse(self, itemId, backwards = False):
        actor     = self.whoHas(itemId)
        showScene = self.scene
        distance  = 0

        if backwards and actor == None:
            return -1

        while None != showScene:
            if showScene.hasActor(actor):
                return distance

            distance += 1

            if backwards:
                showScene = showScene.previous()
            else:
                showScene = showScene.next()
        else:
            return -1

        return distance

    def findMaxDistanceToUse(self, itemSet, backwards = False):
        maxDist  = -1
        maxItems = set()

        if backwards:
            target = self.previous

            if target is None:
                return 0
        else:
            target = self

        for item in itemSet:
            distance = target.distanceToUse(item, backwards)

            if distance > maxDist:
                maxDist  = distance
                maxItems = set([item])
            elif distance == maxDist:
                maxItems.add(item)

        return (maxDist, maxItems)

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

    # Return items not held or held by actors that never need an item again
    def getAvailable(self):
        items = range(self.plot.cardinality)
        avail = set()

        for item in items:
            if -1 == self.distanceToUse(item):
                avail.add(item)

        return avail

    # Return items that are not needed in this scene
    def getStrictlyAvailable(self):
        showScene      = self.getShowScene()
        available      = set()
        actorsAssigned = set()

        # No pickup for these item IDs...
        for item, actor in enumerate(self.pickups):
            if actor == None:
                available.add(item)
            else:
                actorsAssigned.add(actor)

        # The set of actors who need items in this scene, but do not
        # pickup in this scene. Therefore, the item they already have
        # is _not_ strictly available!
        checkActors = showScene.getActors() - actorsAssigned

        for actor in checkActors:
            trackedItem = self.currentlyHeldBy(actor)

            if trackedItem != None:
                assert trackedItem in available, \
                        "Expected tracked requirement not to be picked up, but item %d <tracked to %s> not available for pickup!" % (current, actor)

                available.remove(trackedItem)

        return available

    # Returns the set of items which are eagerly allocated
    def getEagerlyAllocated(self):
        items = range(self.plot.cardinality)
        eager = set()

        for item in items:
            if self.isEagerlyAllocated(item):
                eager.add(item)

        return eager

    def isEagerlyAllocated(self, item):
        # An item is eagerly allocated if it is allocated in this
        # scene or prior, but it is not used in the show between the
        # point of allocation and the point of use.
        actor = self.whoHas(item)

        if actor is None:
            return False

        plScene = self.findPriorPickup(item)

        if plScene is None:
            return False

        pickupShowScene  = plScene.getShowScene()
        currentShowScene = self.getShowScene()
        targetScene      = pickupShowScene

        while True:
            if targetScene.hasActor(actor):
                return False
            elif targetScene == currentShowScene:
                # Tested from pickup to the current scene, and show
                # hasn't used it yet. The assignment was eager.
                return True

            targetScene = targetScene.next()

            assert targetScene is not None, \
                    "Hit end of show whilst scanning for eager usage"

    def findPriorPickup(self, item):
        target = self

        while target is not None:
            if target.pickupInScene(item):
                return target

            target = target.previous

        return None

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
        pickups   = self.getPickups()
        pickupStr = ''

        for item, actor in pickups.iteritems():
            pickupStr += ' <%d>: %s,' % (item, actor)

        return 'Scene[%s:%s] =>%s' % (self.scene.id,
                                       self.scene.name,
                                       pickupStr)
