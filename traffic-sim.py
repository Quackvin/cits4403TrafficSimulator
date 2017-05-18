import Tkinter as tk
import time, math, random, sys

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
    def __init__(self, start_x, start_y, length, direction, road_tag, num_lanes, lane_num, isOncoming, speed_limit):
        self.tags = road_tag

        self.start_point_x = start_x
        self.start_point_y = start_y
        self.length = length
        self.direction = direction
        self.dirc = directions[self.direction]

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
            if self.isOncoming:
                canvas.create_rectangle(
                    (self.draw_start_point_x, self.draw_start_point_y, self.draw_end_point_x, self.draw_end_point_y),
                    width=lane_border, outline='black', fill=reverse_lane_col, tags=self.tags)
            else:
                canvas.create_rectangle(
                    (self.draw_start_point_x, self.draw_start_point_y, self.draw_end_point_x, self.draw_end_point_y),
                    width=lane_border, outline='black', fill=forward_lane_col, tags=self.tags)

    def flip_oncoming(self):
        # flips direction of road and starting point if its an oncoming lane
        if self.isOncoming:
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
        isOncoming = False

        # Offset is determined by if road has even or odd number of lanes
        offset = self.get_lane_offset(self.num_lanes)

        for i in xrange(0, self.num_lanes):
            if self.is_2way and i == self.num_lanes / 2:
                isOncoming = True

            self.lanes.append(
                Lane(self.start_x - (self.dirc[1] * offset), self.start_y + (self.dirc[0] * offset), self.length,
                     self.direction, self.road_tag, self.num_lanes,
                     lane_num, isOncoming, self.speed_limit))
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
        #Study on acceleration and deceleration
        # http://www.academia.edu/7840630/Acceleration-Deceleration_Behaviour_of_Various_Vehicle_Types

#all speeds and the like should be multiplied by scale

        # should all be random (need realistic ranges)
        self.speeding_attitude = 0
        # should be random centered around speed limit
        self.max_speed = float(self.get_lane().speed_limit)*random.randrange(8,15)/10
        #speed car want to turn at
        self.turning_speed = 1.5 *random.randrange(8,15)/10
        self.max_acceleration = float(3)*random.randrange(8,15)/10 #m/s^2
        self.breaking_capacity = float(3)*random.randrange(8,15)/10 #should be relative to speed
        self.reaction_time = 2
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
        # move
        canvas.move(self.rect, self.speed_xy[0], self.speed_xy[1])
        if show_nose:
            canvas.move(self.nose, self.speed_xy[0], self.speed_xy[1])
        self.write_distance_travelled(self.read_distance_travelled() + self.read_speed())

        # other things
        '''
        if critical:
            if tend_change_lanes:
                if can_change_lanes:
                    change_lanes
                else:
                    if can_brake:
                        brake()
                    else:
                        collision()
            else:
                if can_brake:
                    brake()
                else:
                    collision()
        else:
            accelerate()
            if speed_>_max:
                speed = max
        '''
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

        if self.read_distance_travelled() + car_length > self.get_lane().length:
            self.write_speed(self.turning_speed)

        # if you're close to, but not inside the car infront, match their speed
        if self.get_lane_car_infront(self.lane_num) != None \
                and abs(self.read_speed() - self.get_lane_car_infront(self.lane_num).read_speed()) <= self.breaking_capacity \
                and self.get_lane_car_infront(self.lane_num).read_distance_travelled() - self.read_distance_travelled() < 2 * self.courage \
                and self.get_lane_car_infront(self.lane_num).read_distance_travelled() - self.read_distance_travelled() > self.courage:
            self.write_speed(self.get_lane_car_infront(self.lane_num).read_speed())

    def is_critical(self):
        car_infront = self.get_lane_car_infront(self.read_lane_num())
        dist_to_intersection = self.get_distance_to_next_intersection()

        # if 3 car lengths from intersection and above turning speed return true
        if dist_to_intersection < self.courage*3 and self.read_speed() > self.turning_speed:
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
            # if there is a car infront, but the intersection is closer

        else:
            critical_dist = dist_to_intersection
                # decelerates more as it gets closer
            deceleration = ((self.courage / self.breaking_capacity) * critical_dist) / (critical_dist * critical_dist)

                # dont go below turning speed
            if self.next_speed < self.turning_speed:
                self.write_speed(self.turning_speed)

        # if there is no car infront
        self.write_speed(self.read_speed() - deceleration)

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

    # doesnt always detect car
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

    # working, needs tuning
    def next_road(self):
        if eval(self.road_tag).lanes[self.read_lane_num()].isOncoming:
            next_road = eval(eval(self.road_tag).prev_roads[self.next_direction])
        else:
            next_road = eval(eval(self.road_tag).next_roads[self.next_direction])

<<<<<<< HEAD
        #print 'current road starting pos: ', self.get_lane().start_point_x, self.get_lane().start_point_y
        #print 'next road starting pos: ', next_road.lanes[self.lane_num].start_point_x, next_road.lanes[self.lane_num].start_point_y
=======
>>>>>>> 9e2a1d2c9c2a45e2187e2604265b52622c74af51



        self.current_road_end_pos = [self.get_lane().end_point_x, self.get_lane().end_point_y]
        self.next_road_start_pos = [next_road.lanes[self.lane_num].start_point_x, next_road.lanes[self.lane_num].start_point_y]
        print 'current road end pos: ', self.current_road_end_pos[0], self.current_road_end_pos[1]
        print 'next road starting pos: ', self.next_road_start_pos[0], self.next_road_start_pos[1] 
        intersection_distance = abs(self.next_road_start_pos[0] - self.current_road_end_pos[0])
        
        if (intersection_distance < self.get_road().num_lanes * lane_width):
            #print 'now enter the intersection part!!!'
            if(self.current_road_end_pos[0] == self.next_road_start_pos[0]):
                print 'Go vertical line'
                # add action
            elif (self.current_road_end_pos[1] == self.next_road_start_pos[1]):
                print 'Go horizontal line'
                #add action
            elif(self.current_road_end_pos[0] != self.next_road_start_pos[0] | self.current_road_end_pos[1]!=self.next_road_start_pos[1]):
                #print 'intersection distance is: ', intersection_distance
                current_dirc = self.get_lane().dirc
                next_direction = next_road.lanes[self.read_lane_num()].direction
                next_dirc = directions[next_direction]
                intersect_centre_x = self.current_road_end_pos[0] * abs(current_dirc[1]) + self.next_road_start_pos[0] * abs(next_dirc[1])
                intersect_centre_y = self.current_road_end_pos[1] * abs(current_dirc[0]) + self.next_road_start_pos[1] * abs(next_dirc[0])
                self.intersection_centre_pos = [intersect_centre_x, intersect_centre_y]
                print 'intersection pos is: ', self.intersection_centre_pos[0], self.intersection_centre_pos[1]
                speed = self.turning_speed
                interval = 0.025 # one secon
                radius1 = self.intersection_centre_pos[0] - self.current_road_end_pos[0]
                radius2 = self.intersection_centre_pos[1] - self.current_road_end_pos[1]
                radius = radius1 if(radius1 != 0) else radius2
                print 'radius of circle is： ', radius
        
        
        
        self.road_tag = next_road.road_tag
        self.write_distance_travelled(0)
        self.advance_distance_travelled()

        self.direction = next_road.lanes[self.read_lane_num()].direction
        self.dirc = directions[self.direction]

        # car randomly chooses which road to take next out of the next roads given
        self.next_direction = random.randrange(0, len(self.get_road().next_roads))

        # move car to next road (right now it teleports)

        canvas.delete(self.rect)
        if show_nose:
            canvas.delete(self.nose)
        self.draw_car()

# working, needs tuning
def move_cars(cars_array):
    for i in cars_array:
        i.move()
        # need function that gives the right adjusted distance based on prev and next roads
        # lane_num*lane_width creates lets the car travel a little further so it looks like it getting to the lane it wants
        # adjustment only works for counter clockwise
        adjusted_dist = i.read_distance_travelled() + car_length

        if adjusted_dist >= eval(i.road_tag).length:
            i.next_road()
    for i in cars_array:
        i.advance()

cars = []

road1 = Road(200, 400, 300, 0, 'road1', 2, 10)
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
#cars.append(Car('private_car', 'road1', 0, offset=0))


# test small circuit
'''road1 = Road(700, 700, 400, 2, 'road1', 2, 10)
road2 = Road(700, 200, 400, 3, 'road2', 2, 10, prev_roads=['road1'])
road3 = Road(700, 200, 400, 0, 'road3', 2, 10, prev_roads=['road2'])
road4 = Road(700, 200, 400, 1, 'road4', 2, 10, prev_roads=['road3'])

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
cars.append(Car('private_car', 'road4', 0, offset=20))'''

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

for t in range(1000000):
    time.sleep(0.025)
    move_cars(cars)
    canvas.update()

    #sys.stdout.write('max deceleration : not max ratio- %.5f \r' % (ratio1/ratio2))
    #sys.stdout.flush()


root.mainloop()
