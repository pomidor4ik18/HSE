import pygame as pg

class Button():
    """
    Класс Button представляет интерактивную кнопку в игре.
    """

    def __init__(self, x, y, image, single_click):
        """
        Инициализация кнопки.

        Args:
            x (int): Координата X для размещения кнопки.
            y (int): Координата Y для размещения кнопки.
            image (pygame.Surface): Изображение кнопки.
            single_click (bool): Определяет, срабатывает ли кнопка только один раз при нажатии.
        """
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False
        self.single_click = single_click

    def draw(self, surface):
        """
        Отображение кнопки на экране и обработка её нажатий.

        Args:
            surface (pygame.Surface): Поверхность, на которой будет отображаться кнопка.

        Returns:
            bool: True, если кнопка была нажата, иначе False.
        """
        action = False
        # Получение позиции мыши
        pos = pg.mouse.get_pos()

        # Проверка наведения мыши и условий нажатия
        if self.rect.collidepoint(pos):
            if pg.mouse.get_pressed()[0] == 1 and not self.clicked:
                action = True
                # Если кнопка однократного нажатия, устанавливаем флаг clicked
                if self.single_click:
                    self.clicked = True

        # Сброс флага clicked при отпускании кнопки мыши
        if pg.mouse.get_pressed()[0] == 0:
            self.clicked = False

        # Отрисовка кнопки на экране
        surface.blit(self.image, self.rect)

        return action
