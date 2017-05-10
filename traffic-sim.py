import Tkinter as tk
import time, math, random

Main_Road_Width= 1000
Main_Road_Height = 1000

lane_width = 40 #40
lane_border = 4 #4
lane_colour = 'gray'

car_length = 30 #30
car_width = 20 #20

#for switching old and new values
tick = True

#debugging
show_nose = True
lane_colours = True
show_lane_start = True
show_road_start = True

forward_lane_col = 'green'
reverse_lane_col = 'yellow'

root=tk.Tk()
root.title("Traffic Congestion Simulation")
canvas = tk.Canvas(root, width=Main_Road_Width, height=Main_Road_Height, bg="#FFFFFF")
canvas.pack()

class Lane():
    def __init__(self, start_x, start_y, length, direction, road_tag, num_lanes, lane_num, isOncoming, speed_limit):
        self.tags = road_tag

        self.start_point_x = start_x
        self.start_point_y = start_y
        self.length = length
        self.direction = direction

        self.num_lanes = num_lanes
        self.lane_num = lane_num
        self.prev_road_offset = 0

        self.isOncoming = isOncoming

        self.speed_limit = speed_limit

        self.flip_oncoming()
        self.draw_lane()
        if show_lane_start:
            self.draw_ends()

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

        if not lane_colours:
            canvas.create_rectangle(
                (self.draw_start_point_x, self.draw_start_point_y, self.draw_end_point_x, self.draw_end_point_y),
                width=lane_border, outline='black', fill=lane_colour, tags=self.tags)
        else:
            if self.isOncoming:
                canvas.create_rectangle(
                    (self.draw_start_point_x, self.draw_start_point_y, self.draw_end_point_x, self.draw_end_point_y),
                    width=lane_border, outline='black', fill=reverse_lane_col, tags=self.tags)
            else:
                canvas.create_rectangle(
                    (self.draw_start_point_x, self.draw_start_point_y, self.draw_end_point_x, self.draw_end_point_y),
                    width=lane_border, outline='black', fill=forward_lane_col, tags=self.tags)

    def flip_oncoming(self):
        #flips direction of road and starting point if its an oncoming lane
        if self.isOncoming:
            if self.direction == 'right':
                self.direction = 'left'
                self.start_point_x = self.start_point_x + self.length
            elif self.direction == 'left':
                self.direction = 'right'
                self.start_point_x = self.start_point_x - self.length
            elif self.direction == 'down':
                self.direction = 'up'
                self.start_point_y = self.start_point_y + self.length
            elif self.direction == 'up':
                self.direction = 'down'
                self.start_point_y = self.start_point_y - self.length

    #debugging purposes
    def draw_ends(self):
        canvas.create_rectangle(
            (self.start_point_x - 2, self.start_point_y - 2, self.start_point_x + 2, self.start_point_y + 2),
            width=1, outline='black', fill="green"
        )

class Road():
    def __init__(self, start_x, start_y, length, direction, road_tag, num_lanes, speed_limit, is_2way = False, prev_roads = None, next_roads = None):
        self.start_x = start_x
        self.start_y = start_y
        self.length = length
        self.direction = direction
        if prev_roads == None:
            self.prev_roads = []
        else:
            self.prev_roads = prev_roads
        if next_roads == None:
            self.next_roads = []
        else:
            self.next_roads = next_roads

        self.road_tag = road_tag
        self.num_lanes = num_lanes
        self.speed_limit = speed_limit/3.6

        self.is_2way = is_2way
        self.is_2way_check()

        if len(self.prev_roads) == 1:
            self.start_at_prev()
            self.connect_roads(prev_roads[0])

        self.lanes = []
        self.make_road()
        if show_road_start:
            self.draw_ends()

    #autogenerates lanes based on road details. All lanes inherit road attributes
    def make_road(self):
        #how far to shift first lane
        offset = 0

        lane_num = 0

        #if 2way road then after the first half swap direction
        isOncoming = False

        #Offset is determined by if road has even or odd number of lanes
        offset = self.get_lane_offset(self.num_lanes)

        for i in xrange(0, self.num_lanes):
            if self.is_2way and i == self.num_lanes/2:
                isOncoming = True

            if self.direction == 'right':
                self.lanes.append(Lane(self.start_x, self.start_y + offset, self.length, self.direction, self.road_tag, self.num_lanes, lane_num, isOncoming, self.speed_limit))
                lane_num += 1
                offset += lane_width
            elif self.direction == 'left':
                self.lanes.append(Lane(self.start_x, self.start_y - offset, self.length, self.direction, self.road_tag, self.num_lanes, lane_num, isOncoming, self.speed_limit))
                lane_num += 1
                offset += lane_width
            elif self.direction == 'down':
                self.lanes.append(Lane(self.start_x - offset, self.start_y, self.length, self.direction, self.road_tag, self.num_lanes, lane_num, isOncoming, self.speed_limit))
                lane_num += 1
                offset += lane_width
            elif self.direction == 'up':
                self.lanes.append(Lane(self.start_x + offset, self.start_y, self.length, self.direction, self.road_tag, self.num_lanes, lane_num, isOncoming, self.speed_limit))
                lane_num += 1
                offset += lane_width
            else:
                raise Exception('Invalid Direction')

    #lets you make a road starting at end of another
    def start_at_prev(self):
        #only run when creating road based on previous, therefore will only have one prev_road. More can be added later
        prev_road = eval(self.prev_roads[0])

        #this will shift it to the side so the roads arent overlapping
        self_road_offset = self.get_road_offset(self.num_lanes)
        prev_road_offset = self.get_road_offset(prev_road.num_lanes)

        if prev_road.direction == 'right':
            self.start_x = prev_road.start_x + prev_road.length - self_road_offset
            if self.direction == 'down':
                self.start_y = prev_road.start_y - prev_road_offset
            elif self.direction == 'up':
                self.start_y = prev_road.start_y + prev_road_offset
            elif self.direction == 'right':
                self.start_y = prev_road.start_y
            else:
                raise Exception('Cant have roads pointing at eachother (RL)')

        elif prev_road.direction == 'left':
            self.start_x = prev_road.start_x - prev_road.length + self_road_offset
            if self.direction == 'down':
                self.start_y = prev_road.start_y - prev_road_offset
            elif self.direction == 'up':
                self.start_y = prev_road.start_y + prev_road_offset
            elif self.direction == 'left':
                self.start_y = prev_road.start_y
            else:
                raise Exception('Cant have roads pointing at eachother (LR)')

        elif prev_road.direction == 'down':
            self.start_y = prev_road.start_y + prev_road.length - self_road_offset
            if self.direction == 'right':
                self.start_x = prev_road.start_x - prev_road_offset
            elif self.direction == 'left':
                self.start_x = prev_road.start_x + prev_road_offset
            elif self.direction == 'down':
                self.start_x = prev_road.start_x
            else:
                raise Exception('Cant have roads pointing at eachother (DU)')

        elif prev_road.direction == 'up':
            self.start_y = prev_road.start_y - prev_road.length + self_road_offset
            if self.direction == 'right':
                self.start_x = prev_road.start_x - prev_road_offset
            elif self.direction == 'left':
                self.start_x = prev_road.start_x + prev_road_offset
            elif self.direction == 'up':
                self.start_x = prev_road.start_x
            else:
                raise Exception('Cant have roads pointing at eachother (UD)')

        else:
            raise Exception('Invalid Direction')

    #connects previous road to self
    def connect_roads(self, prev_road):
        eval(prev_road).add_next_road(self.road_tag)

    def add_next_road(self, next_road):
        self.next_roads.append(next_road)

    def add_prev_road(self, prev_road):
        self.prev_roads.append(prev_road)

    #offset lines up with center of lane
    def get_lane_offset(self, num_lanes):
        if num_lanes % 2 == 0:
            return -(lane_width / 2) * (num_lanes / 2)
        else:
            return -lane_width * ((num_lanes - 1) / 2)

    #offset lines up with end of lane
    def get_road_offset(self, num_lanes):
        if num_lanes % 2 == 1:
            return -(lane_width * num_lanes) / 2
        else:
            return -lane_width * (num_lanes / 2)

    def is_2way_check(self):
        if self.num_lanes % 2 == 1 and self.is_2way:
            raise Exception('2way Road must have even number of Lanes')

    #for debugging
    def draw_ends(self):
        canvas.create_rectangle(
            (self.start_x - 5, self.start_y - 5, self.start_x + 5, self.start_y + 5),
            width=1, outline='black', fill="red"
        )

class Car():
    def __init__(self, classType, road_tag, lane_num, offset = 0):
        self.car_length = car_length
        self.car_width = car_width
        self.car_class = classType
        self.road_tag = road_tag
        #first value is current, second is new
        self.lane_num = [lane_num, lane_num]
        self.direction = self.get_lane().direction
        #offset is percentage of road length
        #old and new
        self.distance_travelled = [(float(offset)/100) * self.get_lane().length, (float(offset)/100) * self.get_lane().length]
        #old and new
        self.speed = [self.get_lane().speed_limit, self.get_lane().speed_limit]
        self.speed_xy = self.get_speed_components(self.read_speed())

        '''determines which way to turn at intersection
        can be 0/1/2 because intersection can have max 4 roads and one is the road you're going in on'''
        self.next_direction = 0

        '''things the car needs
        - max+speed = 80 + 100 * ln((speeding_attitude * 1.7) + 1)
            - 80 is speed limit
            - 100 is how far over the limit the most daring are willing to go
        - max_acceleration (engine power)
        - max_deceleration (breaking capacity)
        - speeding_attitude (how woll they are to speed)
        - perception_time (reaction time)
        -
        '''

        #should all be random (need realistic ranges)
        self.speeding_attitude = 0
        #should be random centered around speed limit
        self.max_speed = self.get_lane().speed_limit
        self.max_acceleration = 3
        self.breaking_capacity = 6
        self.reaction_time = 2

        self.draw_car()

    #always reading and writing opposites
    def read_speed(self):
        if tick:
            return self.speed[1]
        else:
            return self.speed[0]

    def write_speed(self, speed):
        if tick:
            self.speed[0] = speed
        else:
            self.speed[1] = speed

    def read_lane_num(self):
        if tick:
            return self.lane_num[1]
        else:
            return self.lane_num[0]

    def write_lane_num(self, lane_num):
        if tick:
            self.lane_num[0] = lane_num
        else:
            self.lane_num[1] = lane_num

    def read_distance_travelled(self):
        if tick:
            return self.distance_travelled[1]
        else:
            return self.distance_travelled[0]

    def write_distance_travelled(self, dist):
        if tick:
            self.distance_travelled[0] = dist
        else:
            self.distance_travelled[1] = dist

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
        return self.get_road().lanes[self.read_lane_num()]

    def get_road(self):
        return eval(self.road_tag)

    def draw_car(self):
        if self.direction == 'right':
            self.draw_start_point_x = self.get_lane().start_point_x + self.read_distance_travelled()
            self.draw_start_point_y = self.get_lane().start_point_y - self.car_width/2
            self.draw_end_point_x = self.draw_start_point_x + self.car_length
            self.draw_end_point_y = self.draw_start_point_y + self.car_width
        elif self.direction == 'left':
            self.draw_start_point_x = self.get_lane().start_point_x - self.read_distance_travelled()
            self.draw_start_point_y = self.get_lane().start_point_y + self.car_width/2
            self.draw_end_point_x = self.draw_start_point_x - self.car_length
            self.draw_end_point_y = self.draw_start_point_y - self.car_width
        elif self.direction == 'down':
            self.draw_start_point_x = self.get_lane().start_point_x + self.car_width / 2
            self.draw_start_point_y = self.get_lane().start_point_y + self.read_distance_travelled()
            self.draw_end_point_x = self.draw_start_point_x - self.car_width
            self.draw_end_point_y = self.draw_start_point_y + self.car_length
        elif self.direction == 'up':
            self.draw_start_point_x = self.get_lane().start_point_x - self.car_width / 2
            self.draw_start_point_y = self.get_lane().start_point_y - self.read_distance_travelled()
            self.draw_end_point_x = self.draw_start_point_x + self.car_width
            self.draw_end_point_y = self.draw_start_point_y - self.car_length

        else:
            raise Exception('Invalid Direction')

        self.rect = canvas.create_rectangle(
            (self.draw_start_point_x, self.draw_start_point_y, self.draw_end_point_x, self.draw_end_point_y),
            width=1, outline='black', fill="blue", tags=self.road_tag)

        if show_nose:
            self.nose = canvas.create_rectangle(
                (self.draw_end_point_x, self.draw_end_point_y, self.draw_end_point_x + 3, self.draw_end_point_y + 3),
                width=1, outline='black', fill="green", tags=self.road_tag)

    def move(self):
        canvas.move(self.rect, self.speed_xy[0], self.speed_xy[1])
        if show_nose:
            canvas.move(self.nose, self.speed_xy[0], self.speed_xy[1])
        self.write_distance_travelled(self.read_distance_travelled() + self.read_speed())
        self.accelerate()
        self.change_lanes()

    #need algorithm for this
    def accelerate(self):
        self.get_car_infront()
        self.get_distance_to_next_intersection()
        #
        #
        #
        #
        #
        #
        #
        #
        #
        #
        #
        self.write_speed(self.read_speed())
        self.speed_xy = self.get_speed_components(self.read_speed())

    def get_car_infront(self):
        #gets car infront so its properties can be checked
        #
        #
        #
        #
        #
        return None

    def get_distance_to_next_intersection(self):
        return self.get_road().length - self.read_distance_travelled()

    def change_lanes(self):
        self.check_side_lane(0)
        #decide if want to change lanes
        #check side lane
        #change if can
        #dont change if cant
        #
        #
        #
        #
        #
        return None

    def check_side_lane(self, side):
        #checks if there are cars in lane to side
        #
        #
        #
        return None

    def next_road(self):
        if eval(self.road_tag).lanes[self.read_lane_num()].isOncoming:
            next_road = eval(eval(self.road_tag).prev_roads[self.next_direction])
        else:
            next_road = eval(eval(self.road_tag).next_roads[self.next_direction])
        self.road_tag = next_road.road_tag
        self.distance_travelled = [0,0]

        self.direction = next_road.lanes[self.read_lane_num()].direction
        self.speed_xy = self.get_speed_components(self.read_speed())

        #car randomly chooses which road to take next out of the next roads given
        self.next_direction = random.randrange(0,len(self.get_road().next_roads))

        #move car to next road (right now it teleports)
        #
        #
        #
        canvas.delete(self.rect)
        if show_nose:
            canvas.delete(self.nose)
        self.draw_car()

def move_cars(cars_array):
    for i in cars_array:
        i.move()
        #need function that gives the right adjusted distance based on prev and next roads
        #
        #
        #
        #
        #
        #lane_num*lane_width creates lets the car travel a little further so it looks like it getting to the lane it wants
        # adjustment only works for counter clockwise
        adjusted_dist = i.read_distance_travelled() - i.read_lane_num() * lane_width
        if adjusted_dist >= eval(i.road_tag).length:
            i.next_road()

cars = []

#test small circuit
road1 = Road(700,200,200,'left','road1',2,10)
road2 = Road(700,200,200,'down','road2',2,10, prev_roads=['road1'])
road3 = Road(700,200,200,'right','road3',2,10, prev_roads=['road2'])
road4 = Road(700,200,200,'up','road4',2,10, prev_roads=['road3'])

road4.add_next_road('road1')
road1.add_prev_road('road4')

cars.append(Car('private_car','road1',0, offset=0))
cars.append(Car('private_car','road1',0, offset=40))
cars.append(Car('private_car','road1',0, offset=80))

#testing road ending with 2 directions
'''road1 = Road(500,200,300,'down','road1',2,10, is_2way=True)
road2 = Road(None,None,300,'left','road2',2,10, is_2way=True, prev_roads=['road1'])
road3 = Road(800,200,300,'right','road3',2,10, is_2way=True, prev_roads=['road1'])

road2.add_next_road('road1')
road3.add_next_road('road1')
road1.add_prev_road('road2')
road1.add_prev_road('road3')

cars.append(Car('private_car','road1',0, offset=80))
cars.append(Car('private_car','road1',1, offset=50))'''

#cycling left works
'''road1 = Road(800,200,300,'left','road1',2,10, is_2way=True)
road2 = Road(None, None, 300, 'left', 'road2', 2,10, is_2way=True, prev_roads=['road1'])
road3 = Road(None, None, 100, 'down', 'road3', 2,10, is_2way=True, prev_roads=['road2'])
road4 = Road(None, None, 100, 'down', 'road4', 2,10, is_2way=True, prev_roads=['road3'])
road5 = Road(None, None, 300, 'right', 'road5', 2,10, is_2way=True, prev_roads=['road4'])
road6 = Road(None, None, 300, 'right', 'road6', 2,10, is_2way=True, prev_roads=['road5'])
road7 = Road(None, None, 100, 'up', 'road7', 2,10, is_2way=True, prev_roads=['road6'])
road8 = Road(None, None, 100, 'up', 'road8', 2,10, is_2way=True, prev_roads=['road7'])
road8.add_next_road('road1')
road1.add_prev_road('road8')

cars.append(Car('private_car','road1',0, offset=80))
cars.append(Car('private_car','road2',1, offset=80))'''

#offsets not working for road cycling right
'''road1 = Road(200,200,300,'right','road1',2,10, is_2way=True)
road2 = Road(None, None, 300, 'right', 'road2', 2,10, is_2way=True, prev_roads=['road1'])
road3 = Road(None, None, 100, 'down', 'road3', 2,10, is_2way=True, prev_roads=['road2'])
road4 = Road(None, None, 100, 'down', 'road4', 2,10, is_2way=True, prev_roads=['road3'])
road5 = Road(None, None, 300, 'left', 'road5', 2,10, is_2way=True, prev_roads=['road4'])
road6 = Road(None, None, 300, 'left', 'road6', 2,10, is_2way=True, prev_roads=['road5'])
road7 = Road(None, None, 100, 'up', 'road7', 2,10, is_2way=True, prev_roads=['road6'])
road8 = Road(None, None, 100, 'up', 'road8', 2,10, is_2way=True, prev_roads=['road7'])
road8.add_next_road('road1')
road1.add_prev_road('road8')

cars.append(Car('private_car','road1',0, offset=80))
cars.append(Car('private_car','road2',1, offset=80))'''

for t in range(1000):
    time.sleep(0.025)
    move_cars(cars)
    canvas.update()
    tick = not tick

root.mainloop()
