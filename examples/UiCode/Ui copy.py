from asyncio.windows_events import NULL
from hashlib import new
import anki, asyncio, shiftRegister, pygame
from anki import TrackPieceTypes
import threading

vismap = [[]]
control = anki.Controller()
map = []


def expand_map_to_size(map, width, height):
    current_width = len(map[0])
    current_height = len(map)

    for i in range(width - current_width):
        map.append([])
        pass

    for i in range(height - current_height):
        for column in map: column.append(None)
        pass
    pass

def gen_vismap():
    h_orientation = 1
    v_orientation = 0

    x_position = 0
    y_position = 0

    for i in range(len(map)):
        for s in range(len(vismap)):
            if(len(vismap[s]) <= y_position):
                expand_map_to_size(vismap, len(vismap[s])+1, len(vismap)+1)
        if (map[i].type in (TrackPieceTypes.STRAIGHT,TrackPieceTypes.INTERSECTION)):
            vismap[x_position][y_position] = map[i]
        elif ( map[i].type == TrackPieceTypes.CURVE):
            if map[i].clockwise:
                h_orientation = (h_orientation + 1) % 2
                v_orientation = (v_orientation + 1) % 2
        vismap[x_position][y_position] = map[i]

        x_position += h_orientation
        y_position += v_orientation


def main():
    pygame.init()
    Ui = pygame.display.set_mode((1000,600),pygame.RESIZABLE)
    pygame.display.set_caption("Test")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial",20)
    run = True
    Gerade = pygame.image.load("Gerade.png")
    Kurve = pygame.image.load("Kurve.png")
    Kreuzung = pygame.image.load("Kreuzung.png")
    font = pygame.font.SysFont("Arial",20)
    mapsurface = pygame.Surface((1000, 600)) 
    mapsurface.fill((193, 60, 60))
    mapsurface.blit(Gerade, (0,0))
    autoData = [[pygame.Surface((200,300))],[auto1]]
    
    #gen_vismap()

    while run:
        clock.tick(30)
        Ui.fill((81, 255, 174))
        Ui.blit(mapsurface,(0,0))
        for i in range(len(autoData[0])):
            autoData[0][i].fill((81, 255, 174))
            autodate = font.render("auto1", True, (0,0,0),(255,255,255))
            autoData[0][i].blit(autodate, (0,0))
            autodate = font.render(str(auto1.map_position), True, (0,0,0),(255,255,255))
            autoData[0][i].blit(autodate, (0,50))
            autodate = font.render(str( auto1.current_track_piece), True, (0,0,0),(255,255,255))
            autoData[0][i].blit(autodate, (0,100))
        Ui.blit(autoData[0][0], (1000, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        pygame.display.update()

async def ankiMain(): 
    global auto1
    global map
    auto1 = await control.connect_one()
    await control.scan()
    map = control.map
    await auto1.setSpeed(200)

async def setup():
    asyncio.create_task(ankiMain())
    await asyncio.sleep(10)
    frontend = threading.Thread(target = main)
    frontend.start()
    while True:
        await asyncio.sleep(1000)
        pass
    pass

asyncio.run(setup())

