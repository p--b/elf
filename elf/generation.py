import heapq
import abc
from functools import partial
from elf.plot import Plot
from elf.evaluation import Evaluator

class PlotGenerator:

    def __init__(self, itemClass, act):
        self.act          = act
        self.itemClass    = itemClass
        self.candidates   = []
        self.scenesDone   = 0
        self.scenesTarget = act.size()
        self.printLimit   = 10
        self.__call__     = self.generateAll

    def generateAll(self, selectionSize = 1000):
        self.generateFirst()

        while self.generateNext(selectionSize):
            pass

    def getBestPlots(self, n):
        return heapq.nlargest(n, self.candidates)

    def generateFirst(self):
        if self.scenesDone != 0:
            raise RuntimeError("Cannot generate first; already scenes extant!")

        plot  = Plot(self.itemClass, self.act)
        scene = plot.addNextScene()

        # FIXME: We can't make this
        # initial scene == one candidate
        # assumption if items are inhomogeneous!
        self.seedInitialScene(scene)
        self.recordPlot(self.candidates, plot)
        self.scenesDone += 1

    def generateNext(self, selectionSize):
        if self.scenesDone == self.scenesTarget:
            return False

        newCands = []

        for score, candidate in self.candidates:
            newCands = heapq.merge(newCands, self.getNextGeneration(candidate))

        self.candidates = heapq.nlargest(selectionSize, newCands)
        self.scenesDone += 1

        # FIXME: It's still very possible to get duplicate plots out.
        #        We should find a way of flitering these.

        return True

    def recordPlot(self, target, plot):
        heapq.heappush(target, (Evaluator.runAll(plot), plot))

    def seedInitialScene(self, plotScene):
        showScene = plotScene.getShowScene()

        # FIXME: We should check this against every scene,
        #        until we implement per-actor/scene ranking
        #        (currently we only have binary Y/N)
        if plotScene.plot.cardinality < len(showScene):
            raise RuntimeError("Molto disast: can't cover initial scene! " +
                               "Everything is terrible.")

        item = 0

        # TODO: We should allow seeding from the end-point of a prior act
        for actorSet in self.getEagerActorList(plotScene.plot):
            for actor in actorSet:
                plotScene.pickup(item, actor)
                item += 1

    def getNextGeneration(self, candidate):
        candidate.addNextScene()

        # Timing:
        #   Eager: Get a mic ASAP
        #   Forced: Wait until must-allocate
        forcedList  = self.getForcedActorSet(candidate)
        eagerList   = self.getEagerActorList(candidate, forcedList)
        forcedCands = self.allocateGeneration(candidate, [forcedList])
        eagerCands  = self.allocateGeneration(candidate, eagerList)

        return heapq.merge(forcedCands, eagerCands)

    def allocateGeneration(self, candidate, actorSetList):
        partials = [candidate]

        for actorSet in actorSetList:
            for actor in actorSet:
                newPartials = []

                for partial in partials:
                    newPartials.extend(self.allocateActor(partial, actor))

                partials = newPartials

        children = []

        for partialCandidate in partials:
            self.recordPlot(children, partialCandidate)

        return children

    def allocateActor(self, parentSolution, actor):
        candidates = []

        for alloc in Allocator.getAll():
            if not alloc.enabled:
                continue

            children = alloc(parentSolution, actor)
            candidates.extend(children)

        return candidates

    def getForcedActorSet(self, candidate):
        plotScene = candidate.last()
        actors    = plotScene.getShowScene().getActors()
        forced    = set()

        for actor in actors:
            if None == plotScene.currentlyHeldBy(actor):
                forced.add(actor)

        return forced

    def getEagerActorList(self, candidate, forcedActors = set()):
        #   Visible Set: actors in the X next scenes, increment
        #   X until actors covered N >= plot cardinality. There
        #   is then 1 set when N = plot cardinality, or 1 + nCr
        #   sets where r = N - plot cardinality and n is the
        #   number of actors in the Xth scene from here who don't
        #   have a valid pickup in the Xth scene.
        #   We can't afford to compute nCr sets when r is much
        #   greater than 2, so we should prioritise:
        #      actors with a good 'match' to the r available items (FIXME)
        #      actors with a high 'priority' (FIXME)
        #      actors who need a mic subsequently (FIXME)
        #      ... before picking a number of actors at random.

        eagerList = []
        quota     = candidate.cardinality
        listSum   = 0
        plScene   = candidate.last()
        scene     = plScene.getShowScene()
        current   = plScene.getCurrentAssignments()
        forced    = forcedActors | set(current)

        while listSum < quota:
            # Do not include actors who already have a mic
            actors = scene.getActors() - forced
            forced |= actors
            eagerList.append(actors)
            listSum += len(actors)

            scene = scene.next()

            if scene == None:
                break

        # Trim N to equal plot cardinality
        while listSum > quota:
            eagerList[-1].pop()
            listSum -= 1


        return eagerList

    def __str__(self):
        return "Plots for Act %i:\n" % self.act.id + \
                "\n---\n".join([str(pData[1]) + '\t(= %d)' % pData[0] for pData in self.getBestPlots(self.printLimit)])

class Allocator(object):
    __metaclass__ = abc.ABCMeta
    allocators    = []

    @classmethod
    def getAll(cls):
        if not cls.allocators:
            cls._loadAllocators()

        return cls.allocators

    @classmethod
    def _loadAllocators(cls):
        for alloc in cls.__subclasses__():
            cls.allocators.append(alloc())

    @abc.abstractmethod
    def __call__(self, plot, actor):
        """Allocates the given actor into the given plot at the most recent scene."""

# Any free
class FreeItemAllocator(Allocator):
    enabled = True

    def __call__(self, plot, actor):
        # TODO: some ordering here I think
        # TODO: There is probably some overlap between this and the
        #       LND allocator...
        for item in plot.last().getAvailable():
            newPlot = plot.cloneDiverge()
            newPlot.last().pickup(item, actor)
            return [newPlot]

        return []

# Least-Recently-Used
class LRUAllocator(Allocator):
    enabled = True

    def __call__(self, plot, actor):
        plScene = plot.last()
        itemSet = set(range(plot.cardinality)) & plScene.getStrictlyAvailable()
        plots   = []
        maxDist, maxItems = plScene.findMaxDistanceToUse(itemSet, backwards = True)

        for item in maxItems:
            newPlot = plot.cloneDiverge()
            newPlot.last().pickup(item, actor)
            plots.append(newPlot)

        return plots

# Largest-Next-Distance (only eager assignments)
class LNEagerDAllocator(Allocator):
    enabled = True

    def __call__(self, plot, actor):
        plScene = plot.last()
        items   = plScene.getEagerlyAllocated() & plScene.getStrictlyAvailable()

        plots = []
        maxDist, maxItems = plScene.findMaxDistanceToUse(items)

        for item in maxItems:
            newPlot = plot.cloneDiverge()
            newPlot.last().pickup(item, actor)
            plots.append(newPlot)

        return plots

# Largest-Next-Distance
class LNDAllocator(Allocator):
    enabled = True

    def __call__(self, plot, actor):
        plScene = plot.last()
        items   = set(range(plot.cardinality)) & plScene.getStrictlyAvailable()

        plots = []
        maxDist, maxItems = plScene.findMaxDistanceToUse(items)

        for item in maxItems:
            newPlot = plot.cloneDiverge()
            newPlot.last().pickup(item, actor)
            plots.append(newPlot)

        return plots

# TODO: Random allocator
