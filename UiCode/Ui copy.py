from asyncio.windows_events import NULL
from hashlib import new
import anki, asyncio, shiftRegister, pygame
from anki.const import TrackPieceTypes
from anki import track_pieces

vismap = [[]]
control = anki.Controller()
map = []
async def ankiMain(): 
    global map
    auto1 = await control.connect_one()
    await control.scan()
    map = control.map
#asyncio.run(ankiMain())

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
    mapsurface = pygame.Surface((1000, 600)) 
    mapsurface.fill((193, 60, 60))
    mapsurface.blit(Gerade, (0,0))
    #gen_vismap()

    while run:
        clock.tick(30)
        Ui.fill((81, 255, 174))
        Ui.blit(mapsurface,(0,0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        pygame.display.update()

main()