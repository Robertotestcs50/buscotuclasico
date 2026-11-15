# -*- coding: utf-8 -*-
"""Punto importante de cada foto (x %, y %): el centro del coche, tirando hacia su frontal.
Se usa como object-position en todos los recortes, para que el coche quede centrado igual en toda la web."""
FOCUS = {
    "barco.jpg": (50, 52),
    "car-350z-drift.jpg": (52, 60),
    "car-bmw-325.jpg": (42, 50),
    "car-bmw-drift.jpg": (42, 55),
    "car-bmw.jpg": (38, 60),
    "car-camaro.jpg": (38, 45),
    "car-charger.jpg": (50, 50),
    "car-competition.jpg": (52, 50),
    "car-corvette.jpg": (38, 52),
    "car-mercedes-e500.jpg": (32, 52),
    "car-mercedes-g.jpg": (55, 50),
    "car-mustang-boss.jpg": (38, 60),
    "car-mustang.jpg": (52, 50),
    "car-porsche.jpg": (60, 50),
    "car-range-rover.jpg": (38, 52),
    "car-skyline.jpg": (40, 52),
    "car-supra.jpg": (50, 50),
    "car-urus.jpg": (50, 52),
    "drift-bmw-e36.jpg": (50, 42),
    "drift-bmw-e46.jpg": (52, 60),
    "drift-bmw-m3.jpg": (35, 55),
    "drift-charger.jpg": (55, 52),
    "drift-gt86.jpg": (40, 55),
    "drift-lexus-is200.jpg": (52, 50),
    "drift-lexus-is300.jpg": (62, 58),
    "drift-mustang-gt.jpg": (58, 50),
    "drift-silvia-s13.jpg": (35, 52),
    "drift-silvia-s14.jpg": (55, 55),
    "drift-supra.jpg": (45, 55),
}


def focus_of(img):
    return FOCUS.get(img.replace("-sm.jpg", ".jpg"), (50, 50))
