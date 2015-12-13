import heapq
from elf.plot import Plot
from elf.evaluation import Evaluator

class PlotGenerator:
    def __init__(self, itemClass, act):
        self.act          = act
        self.itemClass    = itemClass
        self.candidates   = []
        self.scenesDone   = 0
        self.scenesTarget = act.size()

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
        newCands = []

        for candidate in self.candidates:
            newCands = heapq.merge(newCands, self.getNextGeneration(candidate))

        self.candidates = heapq.nlargest(selectionSize, newCands)
        self.scenesDone += 1

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

        # TODO: Use an eager generator here
        for actor in showScene.getActors():
            plotScene.pickup(item, actor)
            item += 1

    def getNextGeneration(self, candidate):
        children = []
        # Target Actors:
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
        #      actors who need a mic subsequently
        #      ... before picking a number of actors at random.
        # Timing:
        #   Eager: Get a mic ASAP
        #   Forced: Wait until must-allocate
        # Item Choice:
        #   Any free
        #   Least-Recently-Used
        #   Largest-Next-Distance
        #   Random
        return children

    def __str__(self):
        return "Plots for Act %i:\n" % self.act.id + \
                "\n---\n".join([str(pData[1]) + '\t(@ %d)\n' % pData[0] for pData in self.candidates])
