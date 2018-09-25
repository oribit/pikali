import pygame
import pikali_bag
import time
import sys
from pygame.locals import *

'''
This is a posible idea in case I want to create a proper UI


def draw_dropdown(number, screen, matrix, drop_list, xpo, ypo, width, colour):
    ''
    Draw a drop down object

    :param number: Allow to identify the drop down to draw. If 0 -> new drop down
    :param screen: Screen object to draw in
    :param matrix: Matrix with the position and function to call
    :param drop_list: List to include in the drop down
    :param xpo: X position to draw
    :param ypo: Y position to draw
    :param width: Width for the drop down
    :param colour: Colour of the drop down
    :return:
    ''
    global d_dropdowns
    height = 28

    # In case of a new dropdown we draw it "closed"
    if number == 0 or d_dropdowns[number][0] == 0:
        pygame.draw.rect(screen, colour, (xpo - 1, ypo - 1, width, height), 3)
        pygame.draw.rect(screen, colour, (xpo, ypo, width - 1, height - 1), 1)
        draw_label(screen, drop_list[0], xpo + 5, ypo + 7, 24, colors['yellow'])
        icon = pygame.image.load("imgs/arrow_down.png")
        icon = pygame.transform.scale(icon, (25, 25))
        screen.blit(icon, [xpo + width - 27, ypo])
        matrix.append([xpo + width - 27, ypo, 25, 25, 'dropdown'])
        if number == 0:
            d_dropdowns[len(d_dropdowns) + 1] = [0, drop_list]
    else:
        width = width * 4
        pygame.draw.rect(screen, colour, (xpo - 1, ypo - 1, width, height), 3)
        pygame.draw.rect(screen, colour, (xpo, ypo, width - 1, height - 1), 1)
'''

from vkeyboard import *

pygame.font.init()
pygame.display.init()
#set size of the screen
size = width, height = 480, 320
screen = pygame.display.set_mode(size)

def consumer(text):
    print('Current text : %s' % text)

# Initializes and activates vkeyboard
layout = VKeyboardLayout(VKeyboardLayout.AZERTY)
keyboard = VKeyboard(screen, consumer, layout)
keyboard.enable()


#lista = ['0123456789', 'test2', 'TESTING3', 'test4', 'test5']

#pikali_bag.draw_selection_list(screen, lista, 10, 10, 150, pikali_bag.colors['blue'])

while 1:
    for event in pygame.event.get():
        #ensure there is always a safe way to end the program if the touch screen fails
        keyboard.on_event(event)
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()
    pygame.display.update()
    ## Reduce CPU utilization
    time.sleep(0.1)

