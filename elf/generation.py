import heapq

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

        # We can't make this initial scene == one candidate
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
        heapq.heappush(target, (self.evaluate(plot), plot))

    def evaluate(self, plot):
        # Do all actors requiring mics have them?
        # Total items ever used
        # How many swaps (total)?
        # How many quick-changes?
        # How many concurrent swaps?
        # 'Swappiness' for each owner
        # Are at least n spares available?
        # Standard deviation for a given metric across owners
        return 50

    def seedInitialScene(self, plotScene):
        pass

    def getNextGeneration(self, candidate):
        children = []
        return children
