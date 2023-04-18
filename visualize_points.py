import pygame
import math
import serial
import numpy
import time
import logging
import asyncio
import sys

class VisualiseLidar():
    def __init__(self, addr: str = "/dev/ttyUSB0"): 
        pygame.init()
        self.screen = pygame.display.set_mode((800, 800))
        sysfont = pygame.font.get_default_font()
        font = pygame.font.SysFont(sysfont, 72)

        logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
        
        self.port = self.prepare_port()

        self.dict_distance_angle_quality = {"dist": 0, "angle": 0, "quality": 0}
        self.coordinates = (0, 0)
        self.origin = (400,400)

    def prepare_port(self, addr):
        try:
            port = serial.Serial(addr, baudrate=9600)
            logging.info(f"Serial comm established on {addr}")
            return port

        except serial.serialutil.SerialException:
            logging.error(f"Could no establish serial comm in {addr}", exc_info=True)
            time.sleep(1)
            self.prepare_port(addr)

    async def get_serial_data(self):
        data = self.port.readline()
        data = data.decode("utf-8")
        data = list(map(int, data.split(",")))
        
        self.dict_distance_angle_quality = {"dist": data[0], "angle": data[1], "quality": data[2]}
        logging.info(f"Distance: {data[0]}, Angle: {data[1]}, Quality: {data[2]}")

        await self.update_game_frame()
    
    def interpolate_to_screen(self, distance):
        distance = numpy.interp(distance, (106, 12000), (-350,350), left=-400, right=400)
        return distance
    
    async def calc_coordinates(self):
        angle = self.dict_distance_angle_quality["angle"]
        distance = self.interpolate_to_screen(self.dict_distance_angle_quality["dist"])
        
        x = self.interpolate_to_screen(distance) * math.cos(angle)
        y = self.interpolate_to_screen(distance) * math.sin(angle)
        
        return x, y
    
    async def update_game_frame(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        self.screen.fill(20, 10, 30)
        x, y = await self.calc_coordinates()
        pygame.draw.aaline(self.screen, (0, 255, 0), self.origin, (x + 400, y + 400), 4)
    
        pygame.display.flip()

async def main():
    visualise = VisualiseLidar()
    while True:
        await visualise.get_serial_data()

if __name__ == "__main__":
    asyncio.run(main())


