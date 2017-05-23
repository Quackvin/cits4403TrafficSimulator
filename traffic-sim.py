import Tkinter as tk
import time
import random
import matplotlib, json
matplotlib.use("TkAgg")
from matplotlib import pyplot as plt
from math import pi, sin, cos, tan
from sympy import *

test_name = "64cars2laneNoIntsFullDistPerRoad"


time_sleep = 0.00002 # it is the time interval that canvas update items
turn_num = 1 # it could be 1,2,3. Decide how many steps that a car turn around in 1/4 circle

Main_Road_Width = 1000
Main_Road_Height = 1000

scale = 10

lane_width = 3 * scale  # 40
lane_border = 0.4 * scale  # 4
lane_colour = 'gray'

car_length = 3 * scale  # 30
car_width = 2 * scale  # 20

num_cars = 0

# debugging
show_nose = False
lane_colours = False
show_lane_start = False
show_road_start = False
show_car1 = True
disable_turning = True
slow_ints = False

ratio1 = float(1)
ratio2 = float(1)

forward_lane_col = 'green'
reverse_lane_col = 'yellow'

# a direction will point to one of this list's elements
# order -> [right, down, left, up]
directions = [[1, 0], [0, 1], [-1, 0], [0, -1]]

root = tk.Tk()
root.title("Traffic Congestion Simulation")
canvas = tk.Canvas(root, width=Main_Road_Width, height=Main_Road_Height, bg="#FFFFFF")
canvas.pack()

class Lane():
    def __init__(self, start_x, start_y, length, direction, road_tag, num_lanes, lane_num, is_oncoming, speed_limit):
        self.tags = road_tag

        self.start_point_x = start_x
        self.start_point_y = start_y
        self.length = length
        self.direction = direction
        self.dirc = directions[self.direction]

        self.num_lanes = num_lanes
        self.lane_num = lane_num
        self.prev_road_offset = 0
        self.is_oncoming = is_oncoming

        self.speed_limit = speed_limit

        self.flip_oncoming()
        self.draw_lane()
        if show_lane_start:
            self.draw_ends()

    def draw_lane(self):
        self.draw_start_point_x = self.start_point_x + (self.dirc[1] * (lane_width / 2))
        self.draw_start_point_y = self.start_point_y - (self.dirc[0] * (lane_width / 2))
        self.draw_end_point_x = self.draw_start_point_x + (self.dirc[0] * self.length) - (self.dirc[1] * lane_width)
        self.draw_end_point_y = self.draw_start_point_y + (self.dirc[1] * self.length) + (self.dirc[0] * lane_width)
        
        self.end_point_x = self.draw_end_point_x + (self.dirc[1] * (lane_width / 2))
        self.end_point_y = self.draw_end_point_y - (self.dirc[0] * (lane_width / 2))

        if not lane_colours:
            canvas.create_rectangle(
                (self.draw_start_point_x, self.draw_start_point_y, self.draw_end_point_x, self.draw_end_point_y),
                width=lane_border, outline='black', fill=lane_colour, tags=self.tags)
        else:
            if self.is_oncoming:
                canvas.create_rectangle(
                    (self.draw_start_point_x, self.draw_start_point_y, self.draw_end_point_x, self.draw_end_point_y),
                    width=lane_border, outline='black', fill=reverse_lane_col, tags=self.tags)
            else:
                canvas.create_rectangle(
                    (self.draw_start_point_x, self.draw_start_point_y, self.draw_end_point_x, self.draw_end_point_y),
                    width=lane_border, outline='black', fill=forward_lane_col, tags=self.tags)

    def flip_oncoming(self):
        # flips direction of road and starting point if its an oncoming lane
        if self.is_oncoming:
            self.set_direction((self.direction + 2) % 4)
            self.start_point_x = self.start_point_x - (self.dirc[0] * self.length)
            self.start_point_y = self.start_point_y - (self.dirc[1] * self.length)

    def set_direction(self, direction):
        self.direction = direction
        self.dirc = directions[direction]

    # debugging purposes
    def draw_ends(self):
        canvas.create_rectangle(
            (self.start_point_x - 2, self.start_point_y - 2, self.start_point_x + 2, self.start_point_y + 2),
            width=1, outline='black', fill="green"
        )

class Road():
    def __init__(self, start_x, start_y, length, direction, road_tag, num_lanes, speed_limit, is_2way=False,
                 prev_roads=None, next_roads=None):
        self.start_x = start_x
        self.start_y = start_y
        self.length = length
        self.direction = direction
        self.dirc = directions[self.direction]
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
        self.speed_limit = speed_limit / 3.6

        self.is_2way = is_2way
        self.is_2way_check()

        if len(self.prev_roads) == 1:
            self.start_at_prev()
            self.connect_roads(prev_roads[0])

        self.lanes = []
        self.make_road()
        if show_road_start:
            self.draw_ends()

    # autogenerates lanes based on road details. All lanes inherit road attributes
    def make_road(self):
        # how far to shift first lane
        offset = 0

        lane_num = 0

        # if 2way road then after the first half swap direction
        is_oncoming = False

        # Offset is determined by if road has even or odd number of lanes
        offset = self.get_lane_offset(self.num_lanes)

        for i in xrange(0, self.num_lanes):
            if self.is_2way and i == self.num_lanes / 2:
                is_oncoming = True

            self.lanes.append(
                Lane(self.start_x - (self.dirc[1] * offset), self.start_y + (self.dirc[0] * offset), self.length,
                     self.direction, self.road_tag, self.num_lanes,
                     lane_num, is_oncoming, self.speed_limit))
            lane_num += 1
            offset += lane_width

    # lets you make a road starting at end of another
    def start_at_prev(self):
        # only run when creating road based on previous, therefore will only have one prev_road. More can be added later
        prev_road = eval(self.prev_roads[0])

        # this will shift it to the side so the roads arent overlapping
        self_road_offset = self.get_road_offset(self.num_lanes)
        prev_road_offset = self.get_road_offset(prev_road.num_lanes)

        prev_road_direction = prev_road.direction

        # offset for length of road
        self.start_x = abs(prev_road.dirc[0]) * (
            prev_road.start_x + (prev_road.dirc[0] * (prev_road.length + abs(self_road_offset))))
        self.start_y = abs(prev_road.dirc[1]) * (
            prev_road.start_y + (prev_road.dirc[1] * (prev_road.length + abs(self_road_offset))))

        # offset for width of road
        if self.direction == (prev_road_direction - 1) % 4 or self.direction == (prev_road_direction + 1) % 4:
            self.start_x = (abs(prev_road.dirc[0]) * self.start_x) + abs(prev_road.dirc[1]) * (
                prev_road.start_x - (self.dirc[0] * prev_road_offset))
            self.start_y = (abs(prev_road.dirc[1]) * self.start_y) + abs(prev_road.dirc[0]) * (
                prev_road.start_y - (self.dirc[1] * prev_road_offset))
        elif self.direction == prev_road_direction:
            self.start_x = (abs(prev_road.dirc[0]) * (self.dirc[0] * self.num_lanes * lane_width + self.start_x - abs(self_road_offset))) + (abs(prev_road.dirc[1]) * prev_road.start_x)
            self.start_y = (abs(prev_road.dirc[1]) * (self.dirc[1] * self.num_lanes * lane_width + self.start_y - abs(self_road_offset))) + (abs(prev_road.dirc[0]) * prev_road.start_y)
        else:
            raise Exception('Cant have roads pointing at eachother')

    # connects previous road to self
    def connect_roads(self, prev_road):
        eval(prev_road).add_next_road(self.road_tag)

    def add_next_road(self, next_road):
        self.next_roads.append(next_road)

    def add_prev_road(self, prev_road):
        self.prev_roads.append(prev_road)

    # offset lines up with center of lane
    def get_lane_offset(self, num_lanes):
        if num_lanes % 2 == 0:
            return -(lane_width / 2) * (num_lanes / 2)
        else:
            return -lane_width * ((num_lanes - 1) / 2)

    # offset lines up with end of lane
    def get_road_offset(self, num_lanes):
        if num_lanes % 2 == 1:
            return -(lane_width * num_lanes) / 2
        else:
            return -lane_width * (num_lanes / 2)

    def is_2way_check(self):
        if self.num_lanes % 2 == 1 and self.is_2way:
            raise Exception('2way Road must have even number of Lanes')

    # for debugging
    def draw_ends(self):
        canvas.create_rectangle(
            (self.start_x - 5, self.start_y - 5, self.start_x + 5, self.start_y + 5),
            width=1, outline='black', fill="red"
        )

class Car():
    def __init__(self, classType, road_tag, lane_num, offset=0):
        global num_cars

        self.id = num_cars
        num_cars += 1

        self.car_length = car_length
        self.car_width = car_width
        self.car_class = classType
        self.road_tag = road_tag
        # first value is current, second is new
        self.lane_num = lane_num
        self.next_lane_num = None
        self.direction = self.get_lane().direction
        self.dirc = directions[self.direction]
        # offset is percentage of road length
        # old and new
        self.distance_travelled = (float(offset) / 100) * self.get_lane().length
        self.next_distance_travelled = None
        self.speed = self.get_lane().speed_limit
        self.next_speed = None
        self.speed_xy = self.get_speed_components(self.read_speed())
        self.theta = pi / (2 * turn_num)

        '''determines which way to turn at intersection
        can be 0/1/2 because intersection can have max 4 roads and one is the road you're going in on'''
        self.next_direction = 0
        if eval(self.road_tag).lanes[self.read_lane_num()].is_oncoming:
            self.next_road_value = eval(eval(self.road_tag).prev_roads[self.next_direction])
        else:
            self.next_road_value = eval(eval(self.road_tag).next_roads[self.next_direction])

        #Study on acceleration and deceleration
        # http://www.academia.edu/7840630/Acceleration-Deceleration_Behaviour_of_Various_Vehicle_Types

#all speeds and the like should be multiplied by scale

        # should all be random (need realistic ranges)
        #self.speeding_attitude = 0
        # should be random centered around speed limit
        self.max_speed = float(self.get_lane().speed_limit)*random.randrange(8,15)/10
        #speed car want to turn at
        self.turning_speed = 1.5 *random.randrange(8,15)/10
        self.max_acceleration = float(3)*random.randrange(8,15)/10 #m/s^2
        self.breaking_capacity = float(3)*random.randrange(8,15)/10 #should be relative to speed
        #self.reaction_time = 2
        # how much space they're willing to have behind when changing lanes
        self.courage = float(car_length) + float(1)*random.randrange(0,30)/10

        self.draw_car()

    # always reading and writing opposites
    # if one isnt written they should be the same
    def read_speed(self):
        return self.speed

    def write_speed(self, speed):
        self.next_speed = speed

    #swaps values. Use if doent change so read value is correct
    def advance_speed(self):
        if self.next_speed != None:
            self.speed = self.next_speed
            self.next_speed = None
        self.speed_xy = self.get_speed_components(self.speed)

    def read_lane_num(self, own=True):
        return self.lane_num

    def write_lane_num(self, lane_num):
        self.next_lane_num = lane_num

    def advance_lane_num(self):
        if self.next_lane_num != None:
            self.lane_num = self.next_lane_num
            self.next_lane_num = None

    def read_distance_travelled(self):
        return self.distance_travelled

    def write_distance_travelled(self, dist):
        self.next_distance_travelled = dist

    def advance_distance_travelled(self):
        if self.next_distance_travelled != None:
            self.distance_travelled = self.next_distance_travelled
            self.next_distance_travelled = None

    def advance(self):
        self.advance_distance_travelled()
        self.advance_lane_num()
        self.advance_speed()

    def get_speed_components(self, speed):
        if self.direction == 0:
            return speed, 0
        elif self.direction == 2:
            return -speed, 0
        elif self.direction == 1:
            return 0, speed
        elif self.direction == 3:
            return 0, -speed
        else:
            raise Exception('Invalid Direction')

    def get_lane(self):
        return self.get_road().lanes[self.read_lane_num()]

    def get_road(self):
        return eval(self.road_tag)

    def draw_car(self):
        self.draw_start_point_x = self.get_lane().start_point_x + (self.dirc[0] * self.read_distance_travelled()) - (
        self.dirc[1] * (self.car_width / 2))
        self.draw_start_point_y = self.get_lane().start_point_y + (self.dirc[1] * self.read_distance_travelled()) - (
        self.dirc[0] * (self.car_width / 2))
        self.draw_end_point_x = self.draw_start_point_x + (self.dirc[0] * self.car_length) + (
        self.dirc[1] * self.car_width)
        self.draw_end_point_y = self.draw_start_point_y + (self.dirc[1] * self.car_length) + (
        self.dirc[0] * self.car_width)

        if not show_car1:
            self.rect = canvas.create_rectangle(
                (self.draw_start_point_x, self.draw_start_point_y, self.draw_end_point_x, self.draw_end_point_y),
                width=1, outline='black', fill="blue", tags=self.road_tag)
        else:
            if self.id == 1:
                self.rect = canvas.create_rectangle(
                    (self.draw_start_point_x, self.draw_start_point_y, self.draw_end_point_x, self.draw_end_point_y),
                    width=1, outline='black', fill="purple", tags=self.road_tag)
            else:
                self.rect = canvas.create_rectangle(
                    (self.draw_start_point_x, self.draw_start_point_y, self.draw_end_point_x, self.draw_end_point_y),
                    width=1, outline='black', fill="blue", tags=self.road_tag)

        if show_nose:
            self.nose = canvas.create_rectangle(
                (self.draw_end_point_x, self.draw_end_point_y, self.draw_end_point_x + 3, self.draw_end_point_y + 3),
                width=1, outline='black', fill="green", tags=self.road_tag)

    # working, needs tuning
    def move(self):
        if self.read_distance_travelled() >= self.get_lane().length and not disable_turning:
            self.turn_around()
            self.write_distance_travelled(self.read_distance_travelled() + 1)
        else:
            # move
            canvas.move(self.rect, self.speed_xy[0], self.speed_xy[1])
            if show_nose:
                canvas.move(self.nose, self.speed_xy[0], self.speed_xy[1])
            self.write_distance_travelled(self.read_distance_travelled() + self.read_speed())
    
            
    
            # if critical
            if self.is_critical():
                change_lane_to = self.tend_change_lanes()
                # if wants to change lanes
                if change_lane_to is not False:
                    # if can change lanes
                    if self.can_change_lanes(change_lane_to):
                        # change lanes
                        self.change_lanes(change_lane_to)
                    else:
                        self.decelerate()
    
                # if critical but cant change lanes, decelerate
                else:
                    self.decelerate()
            else:
                # if not critical accelerate
                self.accelerate()
            # dont let speed go beyond max
            if self.next_speed > self.max_speed:
                self.write_speed(self.max_speed)
            # dont let speed to below 0
            if self.next_speed < 0:
                self.next_speed = 0
    
            if slow_ints and self.read_distance_travelled() + car_length > self.get_lane().length:
                self.write_speed(self.turning_speed)
    
            # if you're close to, but not inside the car infront, match their speed
            '''if self.get_lane_car_infront(self.lane_num) != None \
                    and abs(self.read_speed() - self.get_lane_car_infront(self.lane_num).read_speed()) <= self.breaking_capacity \
                    and self.get_lane_car_infront(self.lane_num).read_distance_travelled() - self.read_distance_travelled() < 2 * self.courage \
                    and self.get_lane_car_infront(self.lane_num).read_distance_travelled() - self.read_distance_travelled() > self.courage:
                self.write_speed(self.get_lane_car_infront(self.lane_num).read_speed())'''

    def is_critical(self):
        car_infront = self.get_lane_car_infront(self.read_lane_num())
        dist_to_intersection = self.get_distance_to_next_intersection()

        # if 3 car lengths from intersection and above turning speed return true
        if slow_ints and dist_to_intersection < self.courage*3 and self.read_speed() > self.turning_speed:
            return True
        # if there is a car infront and it is close to and slower than you return true
        if car_infront != None:
            if (car_infront.read_distance_travelled() - self.read_distance_travelled()) < (self.courage):
                return True

            if (car_infront.read_distance_travelled() - self.read_distance_travelled()) < (1.2*self.courage):
                return True
        return False

    # working returns lane it wants to change to or False
    def tend_change_lanes(self):
        # wont change lanes close to ends of road
        # Need to make values better, currently if within 3 car lengths of intersection
        if self.get_lane().length - self.read_distance_travelled() < self.courage*2 or self.read_distance_travelled() < self.courage*2:
            return False

        # should check dist to car infront in next lane, if > current lane return true
        car_infront = self.get_lane_car_infront(self.read_lane_num())
        # If no cars infront dont want to change
        if car_infront == None:
            return False

        # look at lanes on either side
        for i in [self.read_lane_num() - 1, self.read_lane_num() + 1]:
            to_lane = None
            to_lane_dist = 0
            # dont look at own lane or lanes going in opposite direction
            if i >= 0 and i < self.get_road().num_lanes and self.get_road().lanes[i].direction == self.direction:
                # get closest car infront in next lane

                side_car_infront = self.get_lane_car_infront(i)
                if side_car_infront != None:
                    # if side_cat_infront is ahead of car_infront and remember that lane and compare it to previous
                    if side_car_infront.read_distance_travelled() > car_infront.read_distance_travelled() \
                            and side_car_infront.read_distance_travelled() > to_lane_dist:
                        to_lane = i
                        to_lane_dist = side_car_infront.read_distance_travelled()
                # there is a car infront but not to the side
                else:
                    return i
            if to_lane != None:
                return to_lane
        return False

    # working, needs tuning
    def can_change_lanes(self, lane):
        side_car_behind = self.get_lane_car_beside(lane)
        # Need to adjust courage to make more sense
        if side_car_behind is None:
            return True
        elif side_car_behind.read_distance_travelled() + self.courage > self.read_distance_travelled():
            return True

        return False

    # working
    def change_lanes(self, lane):
        self.write_lane_num(lane)
        self.advance_lane_num()
        # redraw car in other lane
        canvas.delete(self.rect)
        if show_nose:
            canvas.delete(self.nose)
        self.draw_car()

    # should come to full stop before touching another car
    # implement critial distance where use full breaking
    # should decelerate to match speed of car infront
    def decelerate(self):
        dist_to_intersection = self.get_distance_to_next_intersection()
        car_infront = self.get_lane_car_infront(self.read_lane_num())

        if car_infront != None:
            dist_to_car_infront = car_infront.read_distance_travelled() - self.read_distance_travelled()
            #if car infront is closer than intersection
            if dist_to_car_infront < dist_to_intersection:
                critical_dist = dist_to_car_infront
                # decelerates more as it gets closer
                deceleration = ((self.courage/self.breaking_capacity) * critical_dist) / (critical_dist * critical_dist)

            #break hard if very close and much slower than you
                if critical_dist < (self.courage*2) \
                        and self.read_speed() > car_infront.read_speed():
                    deceleration = self.breaking_capacity

                    self.write_speed(self.read_speed() - deceleration)
                    return True

                self.write_speed(self.read_speed() - deceleration)
                return True

            # if there is a car infront, but the intersection is closer
        if slow_ints:
            critical_dist = dist_to_intersection
                # decelerates more as it gets closer
            deceleration = ((self.courage / self.breaking_capacity) * critical_dist) / (critical_dist * critical_dist)

                # dont go below turning speed
        if slow_ints and self.next_speed < self.turning_speed:
            self.write_speed(self.turning_speed)

        # if there is no car infront
            self.write_speed(self.read_speed() - deceleration)
            return True

    # working, may need tuning
    def accelerate(self):
        #accelerate faster when going faster
        #how fast they accelerate dependant on car
        acceleration = (self.max_acceleration/3) * self.read_speed() * self.read_speed() + 0.5

        if acceleration > self.max_acceleration:
            acceleration = self.max_acceleration

        self.write_speed(self.read_speed() + acceleration)

    # working
    def get_distance_to_next_intersection(self):
        return self.get_road().length - self.read_distance_travelled()

    # working, needs tuning
    def get_lane_car_beside(self, lane):
        # gets car beside so its properties can be checked
        car_beside = None
        closest_car_dist = 10000

        # Needs to take into account  road ahead and behind for edge cases
        for car in cars:
            # same road, not self, in desired lane, ahead of you, closer than current closest
            if car.road_tag == self.road_tag \
                    and car.id != self.id \
                    and car.read_lane_num() == lane \
                    and car.read_distance_travelled() < self.read_distance_travelled() + self.courage \
                    and car.read_distance_travelled() < closest_car_dist:
                closest_car_dist = car.read_distance_travelled()
                car_beside = car
        return car_beside

    def get_lane_car_infront(self, lane):
        # gets car infront so its properties can be checked
        car_infront = None
        closest_car_dist = 1000000

        for car in cars:
            # same road, not self, in right lame, ahead of you, closer than current closest
            if car.road_tag == self.road_tag \
                    and car.id != self.id \
                    and car.read_lane_num() == lane \
                    and car.read_distance_travelled() > self.read_distance_travelled() \
                    and car.read_distance_travelled() < closest_car_dist:
                closest_car_dist = car.read_distance_travelled()
                car_infront = car
        return car_infront
          
    def turn_around(self):
        
        current_road_end_pos = [self.get_lane().end_point_x, self.get_lane().end_point_y]
        next_road_start_pos = [self.next_road_value.lanes[self.lane_num].start_point_x, self.next_road_value.lanes[self.lane_num].start_point_y]
        #print 'current road end pos: ', current_road_end_pos[0], current_road_end_pos[1]
        #print 'next road starting pos: ', next_road_start_pos[0], next_road_start_pos[1] 
        current_dirc = self.get_lane().dirc 
        print 'current dirc is: ', current_dirc
        next_direction = self.next_road_value.lanes[self.read_lane_num()].direction
        next_dirc = directions[next_direction]
        print'next dirc is: ',next_dirc
        intersect_centre_x = current_road_end_pos[0] * abs(current_dirc[1]) + next_road_start_pos[0] * abs(next_dirc[1])
        intersect_centre_y = current_road_end_pos[1] * abs(current_dirc[0]) + next_road_start_pos[1] * abs(next_dirc[0])
        intersection_centre_pos = [intersect_centre_x, intersect_centre_y]
        intersection_centre_pos = intersection_centre_pos
        #print 'intersection pos is: ', intersection_centre_pos[0], intersection_centre_pos[1]
        radius1 = intersection_centre_pos[0] - current_road_end_pos[0]
        radius2 = intersection_centre_pos[1] - current_road_end_pos[1]
        radius = abs(radius1) if(radius1 != 0) else abs(radius2) 
        radius = int(radius /4)
        #print 'radius of circle is: ', radius
        theta = self.theta
        #print '******theta is, slope_width is :', theta, slope_width
        x= Symbol('x')
        y= Symbol('y')
        
         
        #equation_up
        # direction from [0,-1] to [1,0] 
        if(current_dirc == [0,-1] and next_dirc == [1,0]):
            slope_width = tan(pi/2 + theta)
            slope_length = tan(theta)
            
            vector_v_up_x = intersection_centre_pos[0] - radius * cos(theta) - car_width * cos(theta) / 2
            vector_v_up_y = intersection_centre_pos[1] - radius * sin(theta) - car_width * sin(theta) / 2
            
            vector_v_down_x = intersection_centre_pos[0] - radius * cos(theta) + car_width * cos(theta) / 2
            vector_v_down_y = intersection_centre_pos[1] - radius * sin(theta) + car_width * sin(theta) / 2
                                                          
            vector_v_left_x = intersection_centre_pos[0] - radius * cos(theta) - car_length * sin(theta) /2
            vector_v_left_y = intersection_centre_pos[1] - radius * sin(theta) + car_length * cos(theta) /2
                                                          
            vector_v_right_x = intersection_centre_pos[0] - radius * cos(theta) + car_length * sin(theta) /2
            vector_v_right_y = intersection_centre_pos[1] - radius * sin(theta) - car_length * cos(theta) /2
                                                           
        # direction from [1,0] to [0,1] 
        elif(current_dirc == [1,0] and next_dirc == [0,1]):
            slope_width = tan(theta)
            slope_length = tan(pi/2 + theta)
            
            vector_v_up_x = intersection_centre_pos[0] + radius * sin(theta) + car_width * sin(theta) / 2
            vector_v_up_y = intersection_centre_pos[1] - radius * cos(theta) - car_width * cos(theta) / 2 
                                                        
            vector_v_down_x = intersection_centre_pos[0] + radius * sin(theta) - car_width * sin(theta) / 2
            vector_v_down_y = intersection_centre_pos[1] - radius * cos(theta) + car_width * cos(theta) / 2
                                                          
            vector_v_left_x = intersection_centre_pos[0] + radius * sin(theta) - car_length * cos(theta) /2
            vector_v_left_y = intersection_centre_pos[1] - radius * cos(theta) - car_length * sin(theta) /2
                                                          
            vector_v_right_x = intersection_centre_pos[0] + radius * sin(theta) + car_length * cos(theta) /2
            vector_v_right_y = intersection_centre_pos[1] - radius * cos(theta) + car_length * sin(theta) /2    
                                                           
        # direction from [0,1] to [-1,0] 
        elif(current_dirc == [0,1] and next_dirc == [-1,0]):
            slope_width = tan(pi/2 + theta)
            slope_length = tan(theta)
            
            vector_v_up_x = intersection_centre_pos[0] + radius * cos(theta) + car_width * cos(theta) / 2
            vector_v_up_y = intersection_centre_pos[1] + radius * sin(theta) + car_width * sin(theta) / 2
                                                        
            vector_v_down_x = intersection_centre_pos[0] + radius * cos(theta) - car_width * cos(theta) / 2
            vector_v_down_y = intersection_centre_pos[1] + radius * sin(theta) - car_width * sin(theta) / 2
                                                          
            vector_v_left_x = intersection_centre_pos[0] + radius * cos(theta) + car_length * sin(theta) /2
            vector_v_left_y = intersection_centre_pos[1] + radius * sin(theta) - car_length * cos(theta) /2
                                                          
            vector_v_right_x = intersection_centre_pos[0] + radius * cos(theta) - car_length * sin(theta) /2
            vector_v_right_y = intersection_centre_pos[1] + radius * sin(theta) + car_length * cos(theta) /2
                                                           
        # direction from [-1,0] to [0,-1] 
        elif(current_dirc == [-1,0] and next_dirc == [0,-1]):
            slope_width = tan(theta)
            slope_length = tan(pi/2 + theta)
            
            vector_v_up_x = intersection_centre_pos[0] - radius * sin(theta) - car_width * sin(theta) / 2
            vector_v_up_y = intersection_centre_pos[1] + radius * cos(theta) + car_width * cos(theta) / 2
        
            vector_v_down_x = intersection_centre_pos[0] - radius * sin(theta) + car_width * sin(theta) / 2
            vector_v_down_y = intersection_centre_pos[1] + radius * cos(theta) - car_width * cos(theta) / 2
            
            vector_v_left_x = intersection_centre_pos[0] - radius * sin(theta) + car_length * cos(theta) /2
            vector_v_left_y = intersection_centre_pos[1] + radius * cos(theta) + car_length * sin(theta) /2
                                                          
            vector_v_right_x = intersection_centre_pos[0] - radius * sin(theta) - car_length * cos(theta) /2
            vector_v_right_y = intersection_centre_pos[1] + radius * cos(theta) - car_length * sin(theta) /2                                              
        else:
            print 'exception'
            theta_except = pi/4
            slope_width = tan(theta_except)
            slope_length = tan(pi/2 + theta_except)
            
            vector_v_up_x = intersection_centre_pos[0] - radius * sin(theta_except) - car_width * sin(theta_except) / 2
            vector_v_up_y = intersection_centre_pos[1] + radius * cos(theta_except) + car_width * cos(theta_except) / 2
        
            vector_v_down_x = intersection_centre_pos[0] - radius * sin(theta_except) + car_width * sin(theta_except) / 2
            vector_v_down_y = intersection_centre_pos[1] + radius * cos(theta_except) - car_width * cos(theta_except) / 2
            
            vector_v_left_x = intersection_centre_pos[0] - radius * sin(theta_except) + car_length * cos(theta_except) /2
            vector_v_left_y = intersection_centre_pos[1] + radius * cos(theta_except) + car_length * sin(theta_except) /2
                                                          
            vector_v_right_x = intersection_centre_pos[0] - radius * sin(theta_except) - car_length * cos(theta_except) /2
            vector_v_right_y = intersection_centre_pos[1] + radius * cos(theta_except) - car_length * sin(theta_except) /2
            
                                                        
        vector_v_up = [vector_v_up_x, vector_v_up_y]
        b_up = Symbol('b_up')
        equation_vector_v_up = slope_width * vector_v_up[0] +b_up - vector_v_up[1]
        intercept_width_up = solve([equation_vector_v_up], [b_up])
        #print 'intercept for translate_width_up is :', intercept_width_up[b_up]  
        equation_up = slope_width * x + intercept_width_up[b_up] - y
        #print 'equation_up is: ', equation_up
                                                                          
        vector_v_down = [vector_v_down_x, vector_v_down_y]
        b_down = Symbol('b_down')
        equation_vector_v_down = slope_width * vector_v_down[0] +b_down - vector_v_down[1]
        intercept_width_down = solve([equation_vector_v_down], [b_down])
        #print 'intercept for translate_width_down is :', intercept_width_down[b_down]
        equation_down = slope_width * x + intercept_width_down[b_down] - y
        #print 'equation_down is: ', equation_down
      
        vector_v_left = [vector_v_left_x, vector_v_left_y]
        b_left = Symbol('b_left')
        equation_vector_v_left = slope_length * vector_v_left[0] +b_left - vector_v_left[1]
        intercept_length_left = solve([equation_vector_v_left], [b_left])
        #print 'intercept for translate_length_left is :', intercept_length_left[b_left]
        equation_left = slope_length * x + intercept_length_left[b_left] - y
        #print 'equation_left is: ', equation_left
                                 
        vector_v_right = [vector_v_right_x, vector_v_right_y]
        b_right = Symbol('b_right')
        equation_vector_v_right = slope_length * vector_v_right[0] +b_right - vector_v_right[1]
        intercept_length_right = solve([equation_vector_v_right], [b_right])
        #print 'intercept for translate_length_right is :', intercept_length_right[b_right]
        equation_right = slope_length * x + intercept_length_right[b_right] - y
        #print 'equation_right is: ', equation_right
        #stop = time.time()
        start = time.time()
        #poly_point_1
        poly_1 =solve([equation_up, equation_left],[x,y])
        poly_1_x = float(poly_1[x])
        poly_1_y = float(poly_1[y])
        #print 'polygon_point_1:', poly_1[x], poly_1[y]
        
        #poly_point_2
        poly_2 =solve([equation_up, equation_right],[x,y])
        poly_2_x = float(poly_2[x])
        poly_2_y = float(poly_2[y])
        #print 'polygon_point_2:', poly_2[x], poly_2[y]
        
        #poly_point_3
        poly_3 =solve([equation_down, equation_right],[x,y])
        poly_3_x = float(poly_3[x])
        poly_3_y = float(poly_3[y])
        #print 'polygon_point_3:', poly_3[x], poly_3[y]
        
        #poly_point_4
        poly_4 =solve([equation_down, equation_left],[x,y])
        poly_4_x = float(poly_4[x])
        poly_4_y = float(poly_4[y])
        #print 'polygon_point_4:', poly_4[x], poly_4[y]                   
        
        canvas.delete(self.rect)
        if self.id == 1:
            self.rect = canvas.create_polygon(poly_1_x, poly_1_y,poly_2_x, poly_2_y,poly_3_x, poly_3_y,poly_4_x, poly_4_y,width=1, outline='black',fill='purple')
            print'purple'
        else:
            self.rect = canvas.create_polygon(poly_1_x, poly_1_y,poly_2_x, poly_2_y,poly_3_x, poly_3_y,poly_4_x, poly_4_y,width=1, outline='black',fill='blue')
            print 'blue'
        #canvas.move(self.poly,sin(theta),cos(theta))
        #canvas.move(poly,'1.0','1.0')
        #canvas.update_idletasks()
        #canvas.update()
        
        theta += pi / (2*turn_num)
        self.theta = theta
        stop = time.time()
        print'runing seconds: ',str(stop - start)
        
    # working, needs tuning
    def next_road(self):
        # need to delete current car: canvas.delete(current_car)
        canvas.delete(self.rect)
        self.theta = pi / (2 * turn_num)
        self.road_tag = self.next_road_value.road_tag
        self.write_distance_travelled(0)
        self.advance_distance_travelled()  

        self.direction = self.next_road_value.lanes[self.read_lane_num()].direction
        self.dirc = directions[self.direction]

        # car randomly chooses which road to take next out of the next roads given
        self.next_direction = random.randrange(0, len(self.get_road().next_roads))
        
        if eval(self.road_tag).lanes[self.read_lane_num()].is_oncoming:
            self.next_road_value = eval(eval(self.road_tag).prev_roads[self.next_direction])
        else:
            self.next_road_value = eval(eval(self.road_tag).next_roads[self.next_direction])

        # move car to next road (right now it teleports)

        #canvas.delete(self.rect)
        if show_nose:
            canvas.delete(self.nose)
        self.draw_car()

# working, needs tuning
def move_cars(cars_array):
    # each frame add new data point dataset
    global average_distance_data, average_speed_data
    ave_dist_data = [0,0,0,0]
    ave_speed_data = [0,0,0,0]
    ave_dist_added = [1,1,1,1]

    for i in cars_array:
        i.move()

        #record data into last element of list
        if i.get_lane_car_infront(i.lane_num) != None:
            dist_between = i.get_lane_car_infront(i.lane_num).read_distance_travelled() - i.read_distance_travelled()
            if i.road_tag == 'road1':
                    # add up distances between cars
                ave_dist_data[0] += (i.get_lane_car_infront(i.lane_num).read_distance_travelled() - i.read_distance_travelled())
                ave_dist_added[0] += 1
                ave_speed_data[0] += i.read_speed()

            if i.road_tag == 'road2':
                    # add up distances between cars
                ave_dist_data[1] += (
                i.get_lane_car_infront(i.lane_num).read_distance_travelled() - i.read_distance_travelled())
                ave_dist_added[1] += 1
                ave_speed_data[1] += i.read_speed()

            if i.road_tag == 'road3':
                    # add up distances between cars
                ave_dist_data[2] += (
                i.get_lane_car_infront(i.lane_num).read_distance_travelled() - i.read_distance_travelled())
                ave_dist_added[2] += 1
                ave_speed_data[2] += i.read_speed()

            if i.road_tag == 'road4':
                    # add up distances between cars
                ave_dist_data[3] += (
                i.get_lane_car_infront(i.lane_num).read_distance_travelled() - i.read_distance_travelled())
                ave_dist_added[3] += 1
                ave_speed_data[3] += i.read_speed()

                '''ave_dist_data += (
                i.get_lane_car_infront(i.lane_num).read_distance_travelled() - i.read_distance_travelled())
                ave_dist_added += 1

            # add up speeds
            ave_speed_data += i.read_speed()'''

        #go to next road
        if i.read_distance_travelled() >= i.get_lane().length + turn_num:
            i.next_road()

    for i in cars_array:
        i.advance()

    # find average of aggregated data
    # data point represents average distance between cars
    average_distance_data[0].append(ave_dist_data[0] / ave_dist_added[0])
    average_speed_data[0].append(ave_speed_data[0] / num_cars)

    average_distance_data[1].append(ave_dist_data[1] / ave_dist_added[1])
    average_speed_data[1].append(ave_speed_data[1] / num_cars)

    average_distance_data[2].append(ave_dist_data[2] / ave_dist_added[2])
    average_speed_data[2].append(ave_speed_data[2] / num_cars)

    average_distance_data[3].append(ave_dist_data[3] / ave_dist_added[3])
    average_speed_data[3].append(ave_speed_data[3] / num_cars)
    '''average_distance_data.append(ave_dist_data/ave_dist_added)
    average_speed_data.append(ave_speed_data/num_cars)'''


cars = []

average_distance_data = [[],[],[],[]]
average_speed_data = [[],[],[],[]]


'''road1 = Road(200, 400, 300, 0, 'road1', 2, 10)
road2 = Road(700, 200, 200, 1, 'road2', 2, 10, prev_roads=['road1'])
road3 = Road(700, 200, 200, 0, 'road3', 2, 10, prev_roads=['road1'])
road4 = Road(700, 200, 200, 3, 'road4', 2, 10, prev_roads=['road1'])

road1.add_prev_road('road2')
road1.add_prev_road('road3')
road1.add_prev_road('road4')
road2.add_next_road('road1')
road3.add_next_road('road1')
road4.add_next_road('road1')

cars.append(Car('private_car', 'road1', 0, offset=10))
cars.append(Car('private_car', 'road1', 0, offset=0))'''


# test small circuit
road1 = Road(700, 610, 500, 2, 'road1', 2, 10)
road2 = Road(700, 200, 500, 3, 'road2', 2, 10, prev_roads=['road1'])
road3 = Road(700, 200, 500, 0, 'road3', 2, 10, prev_roads=['road2'])
road4 = Road(700, 200, 500, 1, 'road4', 2, 10, prev_roads=['road3'])

road4.add_next_road('road1')
road1.add_prev_road('road4')

cars.append(Car('private_car', 'road1', 0, offset=30))
cars.append(Car('private_car', 'road1', 0, offset=0))
cars.append(Car('private_car', 'road1', 0, offset=50))
cars.append(Car('private_car', 'road1', 0, offset=80))
cars.append(Car('private_car', 'road2', 0, offset=40))
cars.append(Car('private_car', 'road2', 0, offset=60))
cars.append(Car('private_car', 'road2', 0, offset=0))
cars.append(Car('private_car', 'road2', 0, offset=20))
cars.append(Car('private_car', 'road3', 0, offset=20))
cars.append(Car('private_car', 'road3', 0, offset=70))
cars.append(Car('private_car', 'road3', 0, offset=0))
cars.append(Car('private_car', 'road3', 0, offset=40))
cars.append(Car('private_car', 'road4', 0, offset=0))
cars.append(Car('private_car', 'road4', 0, offset=50))
cars.append(Car('private_car', 'road4', 0, offset=80))
cars.append(Car('private_car', 'road4', 0, offset=20))
cars.append(Car('private_car', 'road1', 0, offset=30))
cars.append(Car('private_car', 'road1', 0, offset=0))
cars.append(Car('private_car', 'road1', 0, offset=50))
cars.append(Car('private_car', 'road1', 0, offset=80))
cars.append(Car('private_car', 'road2', 0, offset=40))
cars.append(Car('private_car', 'road2', 0, offset=60))
cars.append(Car('private_car', 'road2', 0, offset=0))
cars.append(Car('private_car', 'road2', 0, offset=20))
cars.append(Car('private_car', 'road3', 0, offset=20))
cars.append(Car('private_car', 'road3', 0, offset=70))
cars.append(Car('private_car', 'road3', 0, offset=0))
cars.append(Car('private_car', 'road3', 0, offset=40))
cars.append(Car('private_car', 'road4', 0, offset=0))
cars.append(Car('private_car', 'road4', 0, offset=50))
cars.append(Car('private_car', 'road4', 0, offset=80))
cars.append(Car('private_car', 'road4', 0, offset=20))
cars.append(Car('private_car', 'road1', 0, offset=30))
cars.append(Car('private_car', 'road1', 0, offset=0))
cars.append(Car('private_car', 'road1', 0, offset=50))
cars.append(Car('private_car', 'road1', 0, offset=80))
cars.append(Car('private_car', 'road2', 0, offset=40))
cars.append(Car('private_car', 'road2', 0, offset=60))
cars.append(Car('private_car', 'road2', 0, offset=0))
cars.append(Car('private_car', 'road2', 0, offset=20))
cars.append(Car('private_car', 'road3', 0, offset=20))
cars.append(Car('private_car', 'road3', 0, offset=70))
cars.append(Car('private_car', 'road3', 0, offset=0))
cars.append(Car('private_car', 'road3', 0, offset=40))
cars.append(Car('private_car', 'road4', 0, offset=0))
cars.append(Car('private_car', 'road4', 0, offset=50))
cars.append(Car('private_car', 'road4', 0, offset=80))
cars.append(Car('private_car', 'road4', 0, offset=20))
cars.append(Car('private_car', 'road1', 0, offset=30))
cars.append(Car('private_car', 'road1', 0, offset=0))
cars.append(Car('private_car', 'road1', 0, offset=50))
cars.append(Car('private_car', 'road1', 0, offset=80))
cars.append(Car('private_car', 'road2', 0, offset=40))
cars.append(Car('private_car', 'road2', 0, offset=60))
cars.append(Car('private_car', 'road2', 0, offset=0))
cars.append(Car('private_car', 'road2', 0, offset=20))
cars.append(Car('private_car', 'road3', 0, offset=20))
cars.append(Car('private_car', 'road3', 0, offset=70))
cars.append(Car('private_car', 'road3', 0, offset=0))
cars.append(Car('private_car', 'road3', 0, offset=40))
cars.append(Car('private_car', 'road4', 0, offset=0))
cars.append(Car('private_car', 'road4', 0, offset=50))
cars.append(Car('private_car', 'road4', 0, offset=80))
cars.append(Car('private_car', 'road4', 0, offset=20))




# testing road ending with 2 directions
'''road1 = Road(500,200,300,1,'road1',4,10, is_2way=True)
road2 = Road(None,None,300,2,'road2',4,10, is_2way=True, prev_roads=['road1'])
road3 = Road(800,200,300,0,'road3',4,10, is_2way=True, prev_roads=['road1'])

road2.add_next_road('road1')
road3.add_next_road('road1')
road1.add_prev_road('road2')
road1.add_prev_road('road3')

cars.append(Car('private_car','road1',0, offset=80))
cars.append(Car('private_car','road1',1, offset=50))'''

# cycling left works
'''road1 = Road(800,200,300,2,'road1',2,17, is_2way=True)
road2 = Road(None, None, 300, 2, 'road2', 2,17, is_2way=True, prev_roads=['road1'])
road3 = Road(None, None, 100, 1, 'road3', 2,11, is_2way=True, prev_roads=['road2'])
road4 = Road(None, None, 100, 1, 'road4', 2,11, is_2way=True, prev_roads=['road3'])
road5 = Road(None, None, 300, 0, 'road5', 2,17, is_2way=True, prev_roads=['road4'])
road6 = Road(None, None, 300, 0, 'road6', 2,17, is_2way=True, prev_roads=['road5'])
road7 = Road(None, None, 100, 3, 'road7', 2,11, is_2way=True, prev_roads=['road6'])
road8 = Road(None, None, 100, 3, 'road8', 2,11, is_2way=True, prev_roads=['road7'])
road8.add_next_road('road1')
road1.add_prev_road('road8')

cars.append(Car('private_car','road1',0, offset=80))
cars.append(Car('private_car','road2',1, offset=80))'''

# offsets not working for road cycling right
'''road1 = Road(200,200,300,0,'road1',2,10, is_2way=True)
road2 = Road(None, None, 300, 0, 'road2', 2,10, is_2way=True, prev_roads=['road1'])
road3 = Road(None, None, 100, 1, 'road3', 2,10, is_2way=True, prev_roads=['road2'])
road4 = Road(None, None, 100, 1, 'road4', 2,10, is_2way=True, prev_roads=['road3'])
road5 = Road(None, None, 300, 2, 'road5', 2,10, is_2way=True, prev_roads=['road4'])
road6 = Road(None, None, 300, 2, 'road6', 2,10, is_2way=True, prev_roads=['road5'])
road7 = Road(None, None, 100, 3, 'road7', 2,10, is_2way=True, prev_roads=['road6'])
road8 = Road(None, None, 100, 3, 'road8', 2,10, is_2way=True, prev_roads=['road7'])
road8.add_next_road('road1')
road1.add_prev_road('road8')

cars.append(Car('private_car','road1',0, offset=80))
cars.append(Car('private_car','road2',1, offset=80))'''

for t in range(10000):
    time.sleep(time_sleep)
    move_cars(cars)
    canvas.update_idletasks()
    canvas.update()

    #sys.stdout.write('max deceleration : not max ratio- %.5f \r' % (ratio1/ratio2))
    #sys.stdout.flush()


data = {'name': test_name ,'speed' : average_speed_data, 'distance' : average_distance_data}

with open('newtrafficData.json', 'r+') as file:
    filedat = file.read()
    if filedat == '' or filedat == '\n':
        file.write(json.dumps([data]))
    else:
        readData = json.loads(filedat)
        readData.append(data)
        j = json.dumps(readData)
        file.seek(0)
        file.write(j)
