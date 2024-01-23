from Классы import *


clock = pg.time.Clock()

window = pg.display.set_mode(WINDOW_SETTINGS)
pg.display.set_caption("Дикий тир")
run = True
backg = pg.image.load("Картинки/Саванна.jpg")
backg = pg.transform.scale(backg, WINDOW_SETTINGS)

gun = Gun(WINDOW_SETTINGS[0] / 2, WINDOW_SETTINGS[1] - GUN_HEIGHT, 'Картинки/Пулемёт.png', GUN_WIDTH, GUN_HEIGHT)
bullets = []

text_points = Text(WINDOW_SETTINGS[0] - 200, 10, 'Очки: ' + str(points[0] + pointsCurrent[0]), FONT_NAME_GAME, FONT_SIZE_GAME, COLOR_MENU, COLOR_MENU)
text_back = Text(0, 0, 'Назад', FONT_NAME_GAME, FONT_SIZE_GAME, COLOR_MENU, COLOR_MENU_ACTIVE)

creation_animals(randint(7, 12))

menu = Menu(WINDOW_SETTINGS[0] / 2 - 75, 150, "Картинки/Саванна.jpg", ["Играть", "Рекорды", "Магазин", "Выход"])
menu.setToMiddleBorder()
menu.update(window)

while run:

    # Выход
    if menu.choice == menu.items[-1].text_str:
        run = False
    menu.reset()

    clock.tick(40)
    mouseX = pg.mouse.get_pos()[0]
    mouseY = pg.mouse.get_pos()[1]
    for event in pg.event.get():
        if event.type == pg.QUIT:  # QUIT - нажатие на крестик
            menu.update(window)
        if event.type == pg.MOUSEMOTION:
            text_back.isActive = False
            if text_back.rect.collidepoint(event.pos):
                text_back.isActive = True

        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                bullets.append(
                    Bullet(gun.x, gun.y, 'Картинки/Пуля.png', BULLET_WIDTH, BULLET_HEIGHT, gun.angle_radians))
                if text_back.isActive:
                    menu.update(window)
    keys = pg.key.get_pressed()
    # Обновление
    gun.update(mouseX, mouseY)
    for bullet in bullets:
        bullet.update(spisok_animals_on_the_screen)
        if not bullet.isAlive:
            bullets.remove(bullet)
    for animal in spisok_animals_on_the_screen:  # обновление данных
        animal.update()
    # Прорисовка
    window.blit(backg, (0, 0))  # прорисовка заднего фона
    for animal in spisok_animals_on_the_screen:  # прорисовка
        animal.draw(window)
    for bullet in bullets:
        bullet.draw(window)
    gun.draw(window)

    text_points.text_str = 'Очки: ' + str(points[0] + pointsCurrent[0])
    text_points.draw(window)
    text_back.draw(window)

    pg.display.update()

connection_BD(pointsCurrent[0])
pg.quit()
