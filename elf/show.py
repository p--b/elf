import collections

class Act:
    def __init__(self, id):
        self.id     = id
        self.scenes = collections.OrderedDict()
        self.show   = None

    def __len__(self):
        return len(self.scenes)

    def addScene(self, scene):
        self.scenes[scene.id] = scene

    def newScene(self, id):
        s = Scene(id, self)
        self.addScene(s)
        return s

    def firstScene(self):
        return self.scenes.items()[0][1]

    def size(self):
        return len(self.scenes)

    def linkScenes(self):
        previous = None

        for scId, scene in self.scenes:
            if previous:
                previous.nextScene = scene

            scene.previousScene = previous
            scene.linked = True

class Scene:
    def __init__(self, id, act):
        self.name = None
        self.id   = id
        self.act  = act
        self.linked = False
        self.previousScene = None
        self.nextScene     = None
        self.actors        = set()

    def __len__(self):
        return len(self.actors)

    def setName(self, name):
        self.name = name

    def addActor(self, actor):
        self.actors.add(actor)

    def addGroup(self, group):
        self.actors |= group

    def getActors(self):
        return self.actors

    def hasActor(self, actor):
        return actor in self.actors

    def next():
        if not self.linked:
            self.act.linkScenes()

        return self.nextScene

    def previous():
        if not self.linked:
            self.act.linkScenes()

        return self.previousScene

class Show:
    def __init__(self, name, company):
        self.name    = mame
        self.company = company
        self.acts    = {}

    def addAct(self, act):
        self.acts[act.id] = act
        act.show          = self

class ActorGroup:
    def __init__(self, id, actors = []):
        self.name   = None,
        self.id     = id
        self.actors = set(actors)
 
    def setName(self, name):
        self.name = name

    def addActors(self, actors):
        self.actors |= set(actors)
