import pygame

Gray = (112, 128, 144)
White = (255, 255, 255)
Black = (0, 0, 0)
width, height = 800, 600
win = pygame.display.set_mode((width, height))
win.fill(White)
pygame.display.set_caption("Chat App")

pygame.font.init()
font = pygame.font.SysFont('Arial', 20)
login_button = font.render('Login', True, Black)
rect = login_button.get_rect(center=(50, 25))
pygame.draw.rect(win, Gray, (5, 15, 100, 25))
win.blit(login_button, rect)
text1 = font.render('Name', True, Black)
rect = text1.get_rect(center=(150, 25))
win.blit(text1, rect)
username_button = font.render('Username', False, Black)
rect = username_button.get_rect(center=(250, 25))
pygame.draw.rect(win, Gray, (200, 15, 100, 25))
win.blit(username_button, rect)
user_input = ''

run = True
while run:
    pygame.display.update()
    pos = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            if 200 < pos[0] < 300 and 15 < pos[1] < 40:
                username_button = font.render('', True, Black)
                rect = username_button.get_rect(center=(250, 25))
                pygame.draw.rect(win, Gray, (200, 15, 100, 25))
                win.blit(username_button, rect)

        if event.type == pygame.KEYDOWN:
            user_input += event.unicode
        text_surface1 = font.render(user_input, True, Black)
        win.blit(text_surface1, (200, 15))
                # for event2 in pygame.event.get():
                #
                #     if event2.type == pygame.KEYDOWN:
                #         user_input += event2.unicode
                #         print(user_input)
                #     text_surface1 = font.render(user_input, True, Black)
                #     win.blit(text_surface1, (200, 15))

pygame.quit()