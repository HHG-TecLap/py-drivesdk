import pygame

def main():
    pygame.init()
    Ui = pygame.display.set_mode((1000, 400))
    pygame.display.set_caption("Test")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial",20)
    run = True
    text = "temp"

    while run:
        clock.tick(30)
        Ui.fill((255, 255, 255))
        test = font.render("test", True, (0,0,0),(255,255,255))#0, 0,0,0, background=(255,255,255))
        Ui.blit(test,(0,0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        pygame.display.update()

main()