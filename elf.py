#!/usr/bin/env python

from elf.people import Actor

a = Actor(4)

class ActorGroup:
    def __init__(self, id, actors = []):
        self.name   = None,
        self.id     = id
        self.actors = set(actors)
 
    def setName(self, name):
        self.name = name

    def addActors(self, actors):
        self.actors |= set(actors)

class Act:
    def __init__(self, id):
        self.id     = id
        self.scenes = {}

    def addScene(self, scene):
        self.scenes[scene.id] = scene

    def newScene(self, id):
        self.addScene(s = Scene(id, self))
        return s

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
 
    def setName(self, name):
        self.name = name

    def addActor(self, actor):
        self.actors |= actor

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
