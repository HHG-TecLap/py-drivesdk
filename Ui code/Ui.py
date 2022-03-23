import anki, asyncio, shiftRegister, pygame
from anki.const import TrackPieceTypes
from anki import track_pieces

def main():
    pygame.init()
    Ui = pygame.display.set_mode((1000, 400))
    pygame.display.set_caption("Test")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial",20)
    run = True