import abc
import math

class Evaluator(object):
    __metaclass__ = abc.ABCMeta
    evaluators    = []

    @classmethod
    def runAll(cls, plot):
        return sum(cls.report(plot).itervalues())

    @classmethod
    def report(cls, plot):
        if not cls.evaluators:
            cls._loadEvaluators()

        return {type(evaler).__name__: evaler.evaluate(plot) * evaler.weight\
                for evaler in cls.evaluators}

    @classmethod
    def _loadEvaluators(cls):
        for evaler in cls.__subclasses__():
            cls.evaluators.append(evaler())

    @abc.abstractmethod
    def evaluate(self, plot):
        """Provides a numeric value to be summed into the plot's score."""

    @abc.abstractproperty
    def weight(self):
        """Defines the weight of the evaluator."""

# Do all actors that require mics have them?
class CoverEvaluator(Evaluator):
    def evaluate(self, plot):
        for scene in plot.scenes:
            showScene = scene.getShowScene()

            for actor in showScene.getActors():
                if None == scene.currentlyHeldBy(actor):
                    return -1

        return 0

    @property
    def weight(self):
        return 1000

# Total items ever used
class MaxUtilisationEvaluator(Evaluator):
    def evaluate(self, plot):
        util  = plot.getUtilisation()
        avail = plot.cardinality
        spare = avail - util

        if util == 0 or spare == 0:
            return 0

        # Offset is so that spare / avail = 1 when optimal - i.e. when
        # only 1 mic is used (util == 0 is clamped above)
        return (spare + 1) / avail

    @property
    def weight(self):
        return 30

# How many swaps (total)?
class TotalSwapsEvaluator(Evaluator):
    def evaluate(self, plot):
        pickups = 0

        for scene in plot.scenes:
            pickups += len(scene)

        # Don't penalise the first pickup!
        pickups -= plot.getUtilisation()
        possible = len(plot) * plot.cardinality

        return -pickups / possible

    @property
    def weight(self):
        return 30

# How many quick-changes?
class QuickChangeEvaluator(Evaluator):
    def evaluate(self, plot):
        qchanges = 0

        # Do not penalise the beginning of the act
        for scene in plot.scenes[1:]:
            for item, actor in scene.getPickups().iteritems():
                forwards  = scene.distanceToUse(item)

                if scene.previous is not None:
                    backwards = scene.previous.distanceToUse(item, backwards = True)
                else:
                    backwards = -1

                delta = (0 == forwards) + (0 == backwards)
                qchanges += delta

        # Set reference of 1 quick-change per scene is -1
        return - qchanges / len(plot)

    @property
    def weight(self):
        return 75

# How many concurrent swaps?
class ConcurrentSwapEvaluator(Evaluator):
    def evaluate(self, plot):
        penaltyFactor   = 0.69315 # ln2 (looks nice)
        penalty         = 0.0

        # Do not penalise the beginning of the act
        for scene in plot.scenes[1:]:
            swaps = len(scene)

            if swaps > 1:
                proportionNoSwap = 1 - (swaps / float(plot.cardinality))
                penalty         += math.pow(proportionNoSwap, -penaltyFactor) - 1

        return - penalty / float(len(plot))

    @property
    def weight(self):
        return 60

# 'Swappiness' for each owner
class SwappinessEvaluator(Evaluator):
    def evaluate(self, plot):
        actScenes  = plot.getActorItems()

        if len(actScenes) == 0:
            return 0

        swappiness = 0

        for actor, itemSet in actScenes.iteritems():
            swappiness += ((len(itemSet) - 1) ** 2) - 1

        # FIXME: Potentially weight this by number of actors?
        #        Then could increase the output weight!
        return -swappiness / len(actScenes)

    @property
    def weight(self):
        return 3

# Are at least n spares available?
class SparesEvaluator(Evaluator):
    def evaluate(self, plot):
        minSpares = 2
        score     = 0.0

        for scene in plot.scenes:
            spare = len(scene.getUnused())

            if spare > 0:
                score += min(spare, minSpares) / float(minSpares)

        return score / float(len(plot))

    @property
    def weight(self):
        return 20

# Standard deviation for a given metric across owners
# (todo)
