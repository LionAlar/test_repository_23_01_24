import pygame as pg
from math import *
from random import randint
from Константы import *
from БД import *

pg.init()
main_font = pg.font.SysFont(FONT_NAME_GAME, FONT_SIZE_GAME)
points = [0]
pointsCurrent = [0]
all_records_list = []
for id, point in get_points():
    all_records_list.append(point)
    points[0] += point
spisok_animals_on_the_screen = []

class Object:
    def __init__(self, x, y, img, w, h, speed):
        self.image = pg.image.load(img)
        self.image = pg.transform.scale(self.image, (w, h))
        # Rect создается с картинки, считая переданные x,y координатами центра
        self.rect = self.image.get_rect(center=[x, y])
        self.speed = speed
        self.w = w
        self.h = h

    def draw(self, canvas):
        canvas.blit(self.image, self.rect)


class ObjectRotatable(Object):
    def __init__(self, x, y, img, w, h, speed):
        super().__init__(x, y, img, w, h, speed)
        self.img_rotated = self.image
        # Rect создается с картинки, считая переданные x,y координатами центра
        self.rect = self.img_rotated.get_rect(center=[x, y])
        self.angle_radians = 0
        self.angle_degrees = 0
        self.speed = speed

    def getAngleDegrees(angle_radians):
        return angle_radians * 180 / pi

    def getAngleRadians(object1X, object1Y, object2X, object2Y):
        katetX = object2X - object1X
        katetY = object2Y - object1Y

        angle_radians = atan2(katetY, katetX)

        return angle_radians

    def getDirection(angle_radians, vector_len):
        return cos(angle_radians) * vector_len, sin(angle_radians) * vector_len

    def draw(self, canvas):
        canvas.blit(self.img_rotated, self.rect)


class Gun(ObjectRotatable):
    def __init__(self, x, y, img, w, h):
        super().__init__(x, y, img, w, h, SPEED)
        self.x = x
        self.y = y

    def update(self, mouseX, mouseY):
        angle_radians = ObjectRotatable.getAngleRadians(self.x, self.y, mouseX, mouseY)
        if -pi < angle_radians < 0:
            # if 0 < angle_radians < pi:
            self.angle_radians = angle_radians
        self.angle_degrees = ObjectRotatable.getAngleDegrees(self.angle_radians)
        self.img_rotated = pg.transform.rotate(self.image, 180 - self.angle_degrees)
        # Rect создается с картинки, считая переданные x,y координатами центра
        self.rect = self.img_rotated.get_rect(center=[self.x, self.y])


class Bullet(ObjectRotatable):
    def __init__(self, x, y, img, w, h, angle_radians):
        super().__init__(x, y, img, w, h, BULLET_SPEED)

        self.angle_radians = angle_radians
        self.angle_degrees = ObjectRotatable.getAngleDegrees(self.angle_radians)

        self.vX, self.vY = ObjectRotatable.getDirection(self.angle_radians, self.speed)

        self.img_rotated = pg.transform.rotate(self.image, -90 - self.angle_degrees)
        # Rect создается с картинки, считая переданные x, y координатами центра
        self.rect = self.img_rotated.get_rect(center=[x, y])
        self.isAlive = True

    def update(self, animals):
        global pointsCurrent
        self.rect.x += self.vX
        self.rect.y += self.vY
        for animal in animals:
            if self.rect.colliderect(animal.rect):
                animal.lives -= 1
                if animal.lives <= 0:
                    pointsCurrent[0] += animal.points
                    animal.lives = animal.start_lives
                    animals.remove(animal)
                    if len(animals) == 0:
                        creation_animals(randint(7, 12))
                self.isAlive = False
        if self.rect.right >= WINDOW_SETTINGS[0]:
            self.isAlive = False
        if self.rect.left <= 0:
            self.isAlive = False
        if self.rect.bottom >= WINDOW_SETTINGS[1]:
            self.isAlive = False
        if self.rect.top <= 0:
            self.isAlive = False


class Animal(ObjectRotatable):
    def __init__(self, x, y, image, w, h, speed, points, lives):
        super().__init__(x, y, image, w, h, speed)
        self.start_lives = lives
        self.x = x
        self.y = y
        self.points = points
        self.lives = lives

    def update(self):
        self.rect.x += self.speed
        if self.speed > 0 and self.rect.left >= WINDOW_SETTINGS[0]:
            self.rect = self.img_rotated.get_rect(center=[self.x, self.y])
        if self.speed < 0 and self.rect.right <= 0:
            self.rect = self.img_rotated.get_rect(center=[self.x, self.y])

    def draw(self, canvas):
        super().draw(canvas)
        text_lives = main_font.render(str(self.lives) + "", False, (0, 0, 0))
        if self.speed > 0:
            canvas.blit(text_lives, (self.rect.x, self.rect.y - 30))
        else:
            canvas.blit(text_lives, (self.rect.right - 30, self.rect.y - 30))


class LandAnimal(Animal):
    def __init__(self, image, w, h, speed, points, lives):
        if speed > 0:
            x = - w
        else:
            x = WINDOW_SETTINGS[0] + w
        super().__init__(x, randint(HORIZONT - h // 2, WINDOW_SETTINGS[1] - h - GUN_HEIGHT), image, w, h,
                         speed, points, lives)

    def resetXY(self):
        self.y = randint(HORIZONT, WINDOW_SETTINGS[1] - self.h - GUN_HEIGHT)
        self.rect = self.img_rotated.get_rect(center=[self.x, self.y])


class Hameleon(LandAnimal):
    def __init__(self, image, w, h, speed, points, lives):
        super().__init__(image, w, h, speed, points, lives)
        self.start = pg.time.get_ticks()
        self.TIME = 3000
        self.count = 0

    def update(self):
        super().update()
        time = pg.time.get_ticks()
        if time - self.start >= self.TIME:
            self.start = pg.time.get_ticks()
            self.count += 1

    def draw(self, canvas):
        if self.count % 2 == 0:
            super().draw(canvas)


class FlyingAnimal(Animal):
    def __init__(self, image, w, h, speed, points, lives):
        if speed > 0:
            x = - w
        else:
            x = WINDOW_SETTINGS[0] + w
        super().__init__(x, randint(0, HORIZONT), image, w, h, speed, points, lives)

    def resetXY(self):
        self.y = randint(0, HORIZONT)
        self.rect = self.img_rotated.get_rect(center=[self.x, self.y])


class Text:
    def __init__(self, x, y, text_str, font_name,
                 font_size, colorRGB, activeColorRGB):
        self.text_str = text_str
        self.font_name = font_name
        self.font_size = font_size
        self.colorRGB = colorRGB
        self.activeColorRGB = activeColorRGB
        self.font = pg.font.SysFont(self.font_name, self.font_size)
        self.text_line = self.font.render(self.text_str, False, self.colorRGB)
        self.rect = self.text_line.get_rect(topleft=[x, y])
        self.isActive = False

    def draw(self, canvas):
        if self.isActive:
            colorRGB = self.activeColorRGB
        else:
            colorRGB = self.colorRGB
        self.text_line = self.font.render(self.text_str, False, colorRGB)
        canvas.blit(self.text_line, self.rect)


class MyWindow:
    def __init__(self, x, y, name_header_img, text_lines, font_name=FONT_NAME_MENU, font_size=FONT_SIZE_MENU, colorRGB=COLOR_MENU, activeColorRGB=COLOR_MENU_ACTIVE):
        self.choice = ""
        self.menuX = x
        self.menuY = y
        noNameItem = Text(0, 0, "NONAME", font_name, font_size, colorRGB, activeColorRGB)
        self.itemH = noNameItem.rect.h
        self.header_img = pg.image.load(name_header_img)
        self.itemsX = x
        self.itemsY = y
        self.items = []
        itemY = self.itemsY
        for text in text_lines:
            self.items.append(Text(self.itemsX, itemY, text, font_name, font_size, colorRGB, activeColorRGB))
            itemY += self.itemH
        self.itemsH = itemY - self.itemsY
        self.itemsW = self.getMaxItemByWidth().rect.w
        self.headerW = self.itemsW * 1.5
        self.headerH = self.itemH * 3
        self.header_img = pg.transform.scale(self.header_img, [self.headerW, self.headerH])
        self.resetItemsY(self.itemsY, self.headerH)
        self.run = True

    def getMaxItemByWidth(self):
        return max(self.items, key=lambda item: item.rect.w)

    def resetItemsY(self, y, padding=0):
        self.itemsY = y + padding
        itemsY = y + padding
        for item in self.items:
            item.rect.y = itemsY
            itemsY += self.itemH

    def resetX(self, x, padding=0):
        self.menuX = x + padding
        self.itemsX = x + padding
        for item in self.items:
            item.rect.x = self.itemsX + padding

    def resetY(self, y):
        self.menuY = y
        self.itemsY = y
        itemsY = y
        for item in self.items:
            item.rect.y = itemsY
            itemsY += self.itemsH

    def setToLeftBorder(self):
        self.resetX(self.menuX)

    def setToRightBorder(self):
        self.menuX += self.itemsW - self.headerW
        for item in self.items:
            item.rect.x = self.itemsX + \
                          (self.itemsW - item.rect.w)

    def setToMiddleBorder(self):
        self.menuX += (self.itemsW - self.headerW) // 2
        for item in self.items:
            item.rect.x = self.itemsX + \
                          (self.itemsW - item.rect.w) // 2

    def draw(self, canvas):
        canvas.blit(self.header_img, [self.menuX, self.menuY])
        for item in self.items:
            item.draw(canvas)

    def update(self, canvas):
        while self.run:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.run = False
                    self.choice = self.items[-1].text_str
                if event.type == pg.MOUSEMOTION:
                    for item in self.items:
                        item.isActive = False
                        if item.rect.collidepoint(event.pos):
                            item.isActive = True
                if event.type == pg.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        for item in self.items:
                            if item.isActive:
                                self.choice = item.text_str
                                self.run = False
            canvas.fill(COLOR_GAME_BACKGROUND)

            self.draw(canvas)

            pg.display.flip()

    def reset(self):
        self.run = True
        self.choice = ""


class Menu(MyWindow):
    def __init__(self, x, y, name_header_img, text_lines, font_name=FONT_NAME_MENU, font_size=FONT_SIZE_MENU, colorRGB=COLOR_MENU, activeColorRGB=COLOR_MENU_ACTIVE):
        super().__init__(x, y, name_header_img, text_lines, font_name, font_size, colorRGB, activeColorRGB)

    def update(self, canvas):
        while self.run:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.run = False
                    self.choice = self.items[-1].text_str
                if event.type == pg.MOUSEMOTION:
                    for item in self.items:
                        item.isActive = False
                        if item.rect.collidepoint(event.pos):
                            item.isActive = True
                if event.type == pg.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        for item in self.items:
                            if item.isActive:
                                # Рекорды
                                if item == self.items[1]:
                                    records.update(canvas)
                                    records.reset()
                                # Магазин
                                elif item == self.items[2]:
                                    shop.update(canvas)
                                    shop.reset()
                                else:
                                    self.choice = item.text_str
                                    self.run = False
            canvas.fill(COLOR_GAME_BACKGROUND)

            self.draw(canvas)

            pg.display.flip()


class Records(MyWindow):
    def __init__(self, x, y, name_header_img, text_lines, font_name=FONT_NAME_RECORDS, font_size=FONT_SIZE_RECORDS, colorRGB=COLOR_MENU, activeColorRGB=COLOR_MENU_ACTIVE):
        super().__init__(x, y, name_header_img, text_lines, font_name, font_size, colorRGB, activeColorRGB)
        self.headerW = self.itemsW * 0.75
        self.headerH = self.itemH * 3
        self.header_img = pg.transform.scale(self.header_img, [self.headerW, self.headerH])

    def update(self, canvas):
        while self.run:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.run = False
                    self.choice = self.items[-1].text_str
                if event.type == pg.MOUSEMOTION:
                    for item in self.items:
                        item.isActive = False
                        if item.rect.collidepoint(event.pos):
                            item.isActive = True
                if event.type == pg.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        for item in self.items:
                            if item.isActive:
                                if item == self.items[-1]:
                                    self.choice = item.text_str
                                    self.run = False
            canvas.fill(COLOR_GAME_BACKGROUND)

            self.draw(canvas)

            pg.display.flip()


animals = [LandAnimal("Картинки/Слон.png", 250, 180, SPEED_ELEPHANT, POINTS_ELEPHANT, LIVES_ELEPHANT),
           LandAnimal("Картинки/Лев.png", 210, 100, SPEED_LION, POINTS_LION, LIVES_LION),
           LandAnimal("Картинки/Тигр.png", 210, 85, SPEED_TIGER, POINTS_TIGER, LIVES_TIGER),
           LandAnimal("Картинки/Тушканчик.png", 40, 40, SPEED_JERBOA, POINTS_JERBOA, LIVES_JERBOA),
           LandAnimal("Картинки/Страус.png", 90, 180, SPEED_OSTRICH, POINTS_OSTRICH, LIVES_OSTRICH),
           LandAnimal("Картинки/Гиена.png", 150, 70, SPEED_HYENA, POINTS_HYENA, LIVES_HYENA),
           LandAnimal("Картинки/Зебра.png", 160, 80, SPEED_ZEBRA, POINTS_ZEBRA, LIVES_ZEBRA),
           LandAnimal("Картинки/Броненосец.png", 70, 20, SPEED_IRONCLAD, POINTS_IRONCLAD, LIVES_IRONCLAD),
           LandAnimal("Картинки/Ехидна.png", 50, 40, SPEED_ECHIDNA, POINTS_ECHIDNA, LIVES_ECHIDNA),
           Hameleon("Картинки/Хамелеон.png", 40, 25, SPEED_CHAMELEON, POINTS_CHAMELEON, LIVES_CHAMELEON),
           FlyingAnimal("Картинки/Ястреб.png", 80, 100, SPEED_HAWK, POINTS_HAWK, LIVES_HAWK)]


def creation_animals(number_of_animals):
    global spisok_animals_on_the_screen
    for i in range(number_of_animals):
        newAnimal = animals[randint(0, len(animals) - 1)]
        newAnimal.resetXY()
        spisok_animals_on_the_screen.append(newAnimal)
    spisok_animals_on_the_screen.sort(key=lambda animal: animal.rect.bottom)


all_records_list.sort(reverse=True)
records_list10 = []
for i in range(len(all_records_list[:10])):
    if i + 1 < 10:
        space = " " * 8
    else:
        space = " " * 7
    records_list10.append("#" + str(i + 1) + space[:len(space) // 2] + "->" + space[len(space) // 2:] + str(all_records_list[:10][i]))
records_list10.append("Назад")
records = Records(WINDOW_SETTINGS[0] / 2 - 50, 10, "Картинки/Рекорды.png", records_list10)

shop = MyWindow(WINDOW_SETTINGS[0] / 2 - 140, 150, "Картинки/Саванна.jpg", ["В разработке", "Назад"])
shop.setToMiddleBorder()
