import Tkinter as tk
import time, math

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
        #self.draw_ends()

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
            raise Exception('Invalid Direction')

        canvas.create_rectangle(
            (self.draw_start_point_x, self.draw_start_point_y, self.draw_end_point_x, self.draw_end_point_y),
            width=4, outline='black', fill="gray", tags=self.tags)

    #debugging purposes
    def draw_ends(self):
        canvas.create_rectangle(
            (self.start_point_x - 5, self.start_point_y - 5, self.start_point_x + 5, self.start_point_y + 5),
            width=1, outline='black', fill="red"
        )

class Road():
    def __init__(self, start_x, start_y, length, direction, road_tag, num_lanes, speed_limit, is_2way):
        self.start_x = start_x
        self.start_y = start_y
        self.length = length
        self.direction = direction
        self.road_tag = road_tag
        self.num_lanes = num_lanes
        self.speed_limit = speed_limit/3.6
        self.is_2way = is_2way

        self.lanes = []
        self.make_road()
        self.draw_ends()

    #autogenerates lanes based on road details. All lanes inherit road attributes
    def make_road(self):
        #return in an array
        #how far to shift first lane
        offset = 0
        lane_num = 0
        #if even number of lanes
        if self.num_lanes % 2 == 0:
            offset = -(lane_width/2) * (self.num_lanes/2)
        else:
            offset = -lane_width * ((self.num_lanes-1)/2)
        if self.direction == 'right':
            for i in xrange(0,self.num_lanes):
                self.lanes.append(Lane(self.start_x, self.start_y + offset, self.length, self.direction, self.road_tag, self.num_lanes, lane_num, self.speed_limit))
                lane_num += 1
                offset += lane_width
        elif self.direction == 'left':
            for i in xrange(0,self.num_lanes):
                self.lanes.append(Lane(self.start_x, self.start_y - offset, self.length, self.direction, self.road_tag, self.num_lanes, lane_num, self.speed_limit))
                lane_num += 1
                offset += lane_width
        elif self.direction == 'down':
            for i in xrange(0,self.num_lanes):
                self.lanes.append(Lane(self.start_x - offset, self.start_y, self.length, self.direction, self.road_tag, self.num_lanes, lane_num, self.speed_limit))
                lane_num += 1
                offset += lane_width
        elif self.direction == 'up':
            for i in xrange(0,self.num_lanes):
                self.lanes.append(Lane(self.start_x + offset, self.start_y, self.length, self.direction, self.road_tag, self.num_lanes, lane_num, self.speed_limit))
                lane_num += 1
                offset += lane_width
        else:
            raise Exception('Invalid Direction')

    def draw_ends(self):
        canvas.create_rectangle(
            (self.start_x - 5, self.start_y - 5, self.start_x + 5, self.start_y + 5),
            width=1, outline='black', fill="red"
        )

class Car():
    def __init__(self, classType, road_tag, lane_num, direction, offset = 0):
        self.car_length = 30
        self.car_width = 20
        self.car_class = classType
        self.road_tag = road_tag
        self.lane_num = lane_num
        self.direction = direction
        self.distance_travelled = offset
        self.speed = eval(road_tag).speed_limit
        self.speed_xy = self.get_speed_components(eval(road_tag).speed_limit)

        print self.get_lane().lane_num

        '''self.speed = canvas.find_withtag(self.tags)
        print 'canvas.find_withtag(self.tags): ', self.speed
        print 'type(canvas.find_withtag(self.tags)): ', type(self.speed)
        print 'canvas.find_withtag(self.tags)[0]: ', self.speed[0]
        print 'type(canvas.find_withtag(self.tags)[0]): ', type(self.speed[0])'''

        self.draw_car()

    def get_speed_components(self, speed):
        if self.direction == 'right':
            return speed, 0
        elif self.direction == 'left':
            return -speed, 0
        elif self.direction == 'down':
            return 0, speed
        elif self.direction == 'up':
            return 0, -speed
        else:
            raise Exception('Invalid Direction')

    def get_lane(self):
        return eval(self.road_tag).lanes[self.lane_num]

    def draw_car(self):
        if self.direction == 'right':
            self.draw_start_point_x = self.get_lane().start_point_x + self.distance_travelled
            self.draw_start_point_y = self.get_lane().start_point_y - self.car_width/2
            self.draw_end_point_x = self.draw_start_point_x + self.car_length
            self.draw_end_point_y = self.draw_start_point_y + self.car_width
        elif self.direction == 'left':
            self.draw_start_point_x = self.get_lane().start_point_x - self.distance_travelled
            self.draw_start_point_y = self.get_lane().start_point_y + self.car_width/2
            self.draw_end_point_x = self.draw_start_point_x - self.car_length
            self.draw_end_point_y = self.draw_start_point_y - self.car_width
        elif self.direction == 'down':
            self.draw_start_point_x = self.get_lane().start_point_x + self.car_width / 2
            self.draw_start_point_y = self.get_lane().start_point_y + self.distance_travelled
            self.draw_end_point_x = self.draw_start_point_x - self.car_width
            self.draw_end_point_y = self.draw_start_point_y + self.car_length
        elif self.direction == 'up':
            self.draw_start_point_x = self.get_lane().start_point_x - self.car_width / 2
            self.draw_start_point_y = self.get_lane().start_point_y - self.distance_travelled
            self.draw_end_point_x = self.draw_start_point_x + self.car_width
            self.draw_end_point_y = self.draw_start_point_y - self.car_length

        else:
            raise Exception('Invalid Direction')

        self.rect = canvas.create_rectangle(
            (self.draw_start_point_x, self.draw_start_point_y, self.draw_end_point_x, self.draw_end_point_y),
            width=1, outline='black', fill="blue", tags=self.road_tag)

    def move(self):
        canvas.move(self.rect, self.speed_xy[0], self.speed_xy[1])

def move_cars(cars_array):
    for i in cars_array:
        i.move()

#lane1 = Lane(0, 80, 1000, 'down', 'main_road', 3, 0, 70)
#main_road = Road(200,200,700,'right','main_road',3,10,False)
right_road = Road(500,500,700,'right','main_road',2,10,False)
left_road = Road(500,500,700,'left','main_road',2,10,False)
down_road = Road(500,500,700,'down','main_road',2,10,False)
up_road = Road(500,500,700,'up','main_road',2,10,False)

cars = []
cars.append(Car('private_car','right_road',0,'right', offset=100))
cars.append(Car('private_car','left_road',0,'left', offset=100))
cars.append(Car('private_car','down_road',0,'down', offset=100))
cars.append(Car('private_car','up_road',0,'up', offset=100))


for t in range(300):
    time.sleep(0.025)
    move_cars(cars)
    canvas.update()

root.mainloop()
