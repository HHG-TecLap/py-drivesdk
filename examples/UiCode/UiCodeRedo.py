import os, sys
sys.path.append(os.getcwd())

import anki, asyncio, pygame
from anki import TrackPieceTypes
import threading
from VisMapGenerator import generate

os.chdir(os.path.dirname(os.path.abspath(__file__))) #warum auch immer das nötig ist


class Ui:
    _fahrzeuge = []
    _run = True
    _map = []
    _visMap = None
    _visMapSurf = None
    _eventList = []
    
    def __init__(self, fahrzeuge: list[anki.Vehicle], map) -> None:
        self._fahrzeuge = fahrzeuge
        self._map = map
        self._visMap = generate(self._map)
        self._thread =  threading.Thread(target=self._UiThread,daemon=True)
        self._thread.start()
    
    def kill(self):
        self._run = False
    
    def expand_map_to_size(map, width, height):
        current_width = len(map[0])
        current_height = len(map)
        for i in range(width - current_width):
            map.append([[]])
            pass
        for i in range(height - current_height):
            for column in map: 
                column.append([])
            pass
        pass
    
    def gen_MapSurface(self, visMap):
        print(visMap)
        Gerade = pygame.image.load("Gerade.png")
        Kurve = pygame.image.load("Kurve.png")
        Kreuzung = pygame.image.load("Kreuzung.png")
        Start = pygame.image.load("Start.png")
        mapSurf = pygame.surface.Surface((len(visMap)*100, len(visMap[0])*100),pygame.SRCALPHA)
        for x in range(len(visMap)):
            for y in range(len(visMap[x])):
                for i in range(len(visMap[x][y])):
                    match visMap[x][y][i].type: #rotating of map pieces to be implemented
                        case TrackPieceTypes.STRAIGHT:
                            mapSurf.blit(Gerade,(x*100,y*100))
                            
                        case TrackPieceTypes.CURVE:
                            mapSurf.blit(Kurve,(x*100,y*100))
                        case TrackPieceTypes.INTERSECTION:
                            mapSurf.blit(Kreuzung,(x*100,y*100))
                        case TrackPieceTypes.START:
                            mapSurf.blit(Start,(x*100,y*100))
                        case TrackPieceTypes.FINISH:
                            pass
                    pass #add object to map
        self._visMapSurf = mapSurf
    
    def addEvent(self, text:str, )
    
    def _UiThread(self):
        pygame.init()
        self.gen_MapSurface(self._visMap)
        font = pygame.font.SysFont("Arial",20)
        Ui = pygame.display.set_mode((1000,600),pygame.SCALED)
        Logo = pygame.image.load("Logo.png")
        pygame.display.set_icon(Logo)
        pygame.display.set_caption("Anki Ui Access")
        clock = pygame.time.Clock()
        run = True
        while(run):
            Ui.fill((100,150,100))
            Ui.blit(self._visMapSurf,(0,0))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
            pygame.display.update()
            clock.tick(60)
    
    pass


async def TestMain():
    print("Start")
    auto1 = await control.connectOne()
    #auto2 = await control.connectOne()
    await control.scan()
    Ui((auto1),control.map)
    while True:
        await asyncio.sleep(100)

try:
    control = anki.Controller()
    asyncio.run(TestMain())
finally:
    control.disconnectAll()