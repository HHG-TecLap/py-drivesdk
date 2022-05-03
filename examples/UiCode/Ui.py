import anki, asyncio, shiftRegister, pygame
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

control = anki.Controller()
map = []
async def ankiMain(): 
    global map
    auto1 = await control.connect_one()
    await control.scan()
    map = control.map
    
asyncio.run(ankiMain())

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

vismap = [[]]
def gen_vismap():
    def insert_at(x_position, y_position, piece) -> tuple[int,int]:
        vis_width = len(vismap)
        vis_height = len(vismap[0])

        if x_position >= vis_width:
            vismap.append([None]*vis_height)
        elif x_position < 0:
            vismap.insert(0,[None]*vis_height)
            x_position += 1

        elif y_position >= vis_height:
            for column in vismap: column.append(None)
        elif y_position < 0:
            for column in vismap: column.insert(0,None)
            y_position += 1
        
        vismap[x_position][y_position] = piece
        
        return x_position, y_position
        pass

    h_orientation = 1
    v_orientation = 0
    ORIENTATION_LOOKUP = (
        (0, 1),
        (1, 0),
        (0,-1),
        (-1,0)
    )

    x_position = 0
    y_position = 0

    for i, piece in enumerate(map):
        x_position, y_position = insert_at(x_position, y_position, piece)

        if piece.type == TrackPieceTypes.CURVE:
            inc = 1 if piece.clockwise else -1
            current_oindex = ORIENTATION_LOOKUP.index((h_orientation,v_orientation))
            current_oindex = (current_oindex + inc) % 4
            h_orientation, v_orientation = ORIENTATION_LOOKUP[current_oindex]
            pass

        x_position += h_orientation
        y_position += v_orientation
        pass

gen_vismap()
print(vismap)

"""def main():
    pygame.init()
    Ui = pygame.display.set_mode((1000,600),pygame.RESIZABLE)
    pygame.display.set_caption("Test")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial",20)
    run = True
    Gerade = pygame.image.load("Gerade.png")
    Kurve = pygame.image.load("Kurve.png")
    Kreuzung = pygame.image.load("Kreuzung.png")
    
    #gen_vismap()

    while run:
        clock.tick(30)
        Ui.fill((81, 255, 174))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        pygame.display.update()

main()"""