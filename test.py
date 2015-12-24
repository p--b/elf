from elf.generation import PlotGenerator
from elf.items import YesItem
from elf.show import Act
from elf.people import Actor

IClass = YesItem("YesClass", 5)
a      = Act(1)

Anthony = Actor(0).setName("Anthony")
Bertie  = Actor(1).setName("Bertie")
Charlie = Actor(2).setName("Charlie")
Daphne  = Actor(3).setName("Daphne")
Ernest  = Actor(4).setName("Ernest")
Fred    = Actor(5).setName("Fred")

s = a.newScene(0)
s.addActor(Anthony)
s.addActor(Bertie)

s = a.newScene(1)
s.addActor(Charlie)
s.addActor(Daphne)

s = a.newScene(2)
s.addActor(Charlie)

s = a.newScene(3)
s.addActor(Ernest)
s.addActor(Fred)

s = a.newScene(4)
s.addActor(Anthony)
s.addActor(Bertie)

G = PlotGenerator(IClass, a)
