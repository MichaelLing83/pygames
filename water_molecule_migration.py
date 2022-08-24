#!/usr/bin/env python3


from time import sleep
from typing import List, Tuple
import pygame as pg
from math import pi
from loguru import logger
import os
from pathlib import Path
from random import randint, random

main_dir: Path = Path(__file__).resolve().parent


def load_image(file):
    """loads an image, prepares it for play"""
    file = os.path.join(main_dir, "data", file)
    try:
        surface = pg.image.load(file)
    except pg.error:
        raise SystemExit(f'Could not load image "{file}" {pg.get_error()}')
    return surface.convert()


RESOLUTION_X = 640 * 2
RESOLUTION_Y = 480 * 2
SCREENRECT = pg.Rect(0, 0, RESOLUTION_X, RESOLUTION_Y)

if pg.get_sdl_version()[0] == 2:
    pg.mixer.pre_init(44100, 32, 2, 1024)
pg.init()
if pg.mixer and not pg.mixer.get_init():
    logger.warning("Warning, no sound")
    pg.mixer = None
font_monospace = pg.font.SysFont("monospace", 15)
fullscreen = False
# Set the display mode
winstyle = pg.SCALED  # 0  # |FULLSCREEN
bestdepth = pg.display.mode_ok(SCREENRECT.size, winstyle, 32)
screen = pg.display.set_mode(
    size=SCREENRECT.size,
    flags=winstyle,
    depth=bestdepth)
h2o_jpg = load_image("H2O.jpg")
pg.display.set_icon(h2o_jpg)
pg.display.set_caption("Pygame Aliens")
WHITE = pg.Color(255, 255, 255)

screen.fill(WHITE)
pg.display.flip()

RED = pg.Color(255, 0, 0)
BLUE = pg.Color(0, 0, 255)
pg.draw.circle(
    surface=screen,
    color=RED,
    center=(5, 5),
    radius=5,
    width=5
)
pg.display.flip()


def in_cell(
    cell: Tuple[int, int, int, int],    # left, top, width, height
    position: Tuple[int, int],     # x, y
    radius: int
) -> bool:
    left, top, width, height = cell
    x, y = position
    if left - radius < x < left + width + radius:
        if top - radius < y < top + height + radius:
            return True
    return False


def pass_cell_wall(
    cell: Tuple[int, int, int, int],    # left, top, width, height
    start: Tuple[int, int],     # x, y
    end: Tuple[int, int],
    radius: int
) -> bool:
    if in_cell(cell, start, radius) != in_cell(cell, end, radius):
        return True
    else:
        return False


def main_event_loop(
    num_molecules: int,
    step: int,
    cell_wall_resist: float = 0.1,
    cell_min_molecule_ratio: float = 0.3,
    molecule_radius: int = 5,
    stop_on_cell_death: bool = True
):
    cell = (RESOLUTION_X // 6, RESOLUTION_Y // 6,
            RESOLUTION_X // 6, RESOLUTION_Y // 6)
    molecules: List[Tuple[int, int]] = [
        (
            randint(cell[0]+molecule_radius, cell[0]+cell[2]-molecule_radius),
            randint(cell[1]+molecule_radius, cell[1]+cell[3]-molecule_radius)
        ) for _ in range(num_molecules)
    ]
    cell_min_molecule_num: float = num_molecules * cell_min_molecule_ratio
    clock = pg.time.Clock()
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
        screen.fill(WHITE)
        # logger.debug(molecules)
        pg.draw.rect(
            surface=screen,
            color=BLUE,
            rect=cell,
            width=2)
        new_molecules = list()
        in_cell_molecule_num: int = len(
            [m for m in molecules if in_cell(cell, m, molecule_radius)]
        )
        cell_is_dead: bool = in_cell_molecule_num < cell_min_molecule_num
        label = font_monospace.render(
            f"Water molecules in cell: {in_cell_molecule_num}, cell is {'dead' if cell_is_dead else 'alive'}",
            1, (25, 4, 95))
        screen.blit(label, (RESOLUTION_X//2-20, RESOLUTION_Y-40))
        for x, y in molecules:
            pg.draw.circle(
                surface=screen,
                color=RED,
                center=(x, y),
                radius=molecule_radius,
                width=molecule_radius
            )
            if (not cell_is_dead) or (not stop_on_cell_death):
                new_x = x + randint(-step, step)
                new_y = y + randint(-step, step)
                if pass_cell_wall(cell, (x, y), (new_x, new_y), molecule_radius):
                    if random() < cell_wall_resist:
                        new_molecules.append((x, y))
                    else:
                        new_molecules.append((new_x, new_y))
                else:
                    new_molecules.append((new_x, new_y))
                # drop the ones moved out of the screen
                new_molecules = [(x, y) for (x, y) in new_molecules if 0 < x
                                 < RESOLUTION_X and 0 < y < RESOLUTION_Y]
                molecules = new_molecules
        pg.display.flip()
        clock.tick(40)


if __name__ == '__main__':
    main_event_loop(
        num_molecules=10,
        step=5
    )
    pg.quit()
