import Tkinter as tk
import time
import math

Main_Road_Width= 1000
Main_Road_Height = 1000

lane_width = 40

root=tk.Tk()
root.title("Traffic Congestion Simulation")
canvas = tk.Canvas(root, width=Main_Road_Width, height=Main_Road_Height, bg="#FFFFFF")
canvas.pack()

class Lane():
    def __init__(self, start_x, start_y, length, direction, road_tag, num_lanes, lane_num, speed_limit):
        self.tags = road_tag

        self.start_point_x = start_x
        self.start_point_y = start_y
        self.length = length
        self.direction = direction

        self.num_lanes = num_lanes
        self.lane_num = lane_num
        self.speed_limit = speed_limit

        self.draw_lane()

    def draw_lane(self):
        if self.direction == 'right':
            self.draw_start_point_x = self.start_point_x
            self.draw_start_point_y = self.start_point_y - lane_width/2
            self.draw_end_point_x = self.start_point_x + self.length
            self.draw_end_point_y = self.draw_start_point_y + lane_width
        elif self.direction == 'left':
            self.draw_start_point_x = self.start_point_x
            self.draw_start_point_y = self.start_point_y + lane_width/2
            self.draw_end_point_x = self.start_point_x - self.length
            self.draw_end_point_y = self.draw_start_point_y - lane_width
        elif self.direction == 'down':
            self.draw_start_point_x = self.start_point_x + lane_width / 2
            self.draw_start_point_y = self.start_point_y
            self.draw_end_point_x = self.draw_start_point_x - lane_width
            self.draw_end_point_y = self.start_point_y + self.length
        elif self.direction == 'up':
            self.draw_start_point_x = self.start_point_x - lane_width / 2
            self.draw_start_point_y = self.start_point_y
            self.draw_end_point_x = self.draw_start_point_x + lane_width
            self.draw_end_point_y = self.start_point_y - self.length

        else:
            return 'direction not recognised'

        canvas.create_rectangle(
            (self.draw_start_point_x, self.draw_start_point_y, self.draw_end_point_x, self.draw_end_point_y),
            width=4, outline='black', fill="gray", tags=self.tags)

#autogenerates lanes based on road details. All lanes inherit road attributes
def make_road(start_x, start_y, length, direction, road_tag, num_lanes, speed_limit, is_2way):
    #return in an array
    lanes = []
    #how far to shift first lane
    offset = 0
    lane_num = 0
    #if even number of lanes
    if num_lanes % 2 == 0:
        offset = (lane_width/2) * (num_lanes/2)
    else:
        offset = lane_width * ((num_lanes-1)/2)
    if direction == 'right':
        for i in xrange(0,num_lanes):
            lanes.append(Lane(start_x, start_y - offset, length, direction, road_tag, num_lanes, lane_num, speed_limit))
            lane_num += 1
            offset += lane_width
    elif direction == 'left':
        for i in xrange(0,num_lanes):
            lanes.append(Lane(start_x, start_y + offset, length, direction, road_tag, num_lanes, lane_num, speed_limit))
            lane_num += 1
            offset -= lane_width
    elif direction == 'down':
        for i in xrange(0,num_lanes):
            lanes.append(Lane(start_x - offset, start_y, length, direction, road_tag, num_lanes, lane_num, speed_limit))
            lane_num += 1
            offset += lane_width
    elif direction == 'up':
        for i in xrange(0,num_lanes):
            lanes.append(Lane(start_x, start_y - offset, length, direction, road_tag, num_lanes, lane_num, speed_limit))
            lane_num += 1
            offset -= lane_width
    else:
        return "error"

    return lanes

#lane1 = Lane(0, 80, 1000, 'down', 'main_road', 3, 0, 70)
make_road(200,200,1000,'right','main_road',3,70,False)


for t in range(300):
    time.sleep(0.025)

root.mainloop()
