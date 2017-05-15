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

num_cars = 0

#debugging
show_nose = True
lane_colours = True
show_lane_start = True
show_road_start = True

forward_lane_col = 'green'
reverse_lane_col = 'yellow'

#a direction will point to one of this list's elements
#order -> [right, down, left, up]
directions = [[1,0], [0,1], [-1,0], [0,-1]]

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
        self.draw_end_point_y = self.draw_start_point_y + (self.dirc[1]*self.length) + (self.dirc[0] * lane_width)

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
            self.set_direction((self.direction + 2) % 4)
            self.start_point_x = self.start_point_x - (self.dirc[0] * self.length)
            self.start_point_y = self.start_point_y - (self.dirc[1] * self.length)

    def set_direction(self, direction):
        self.direction = direction
        self.dirc = directions[direction]

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

            self.lanes.append(
                Lane(self.start_x - (self.dirc[1] * offset), self.start_y + (self.dirc[0] * offset), self.length, self.direction, self.road_tag, self.num_lanes,
                     lane_num, isOncoming, self.speed_limit))
            lane_num += 1
            offset += lane_width

    #lets you make a road starting at end of another
    def start_at_prev(self):
        #only run when creating road based on previous, therefore will only have one prev_road. More can be added later
        prev_road = eval(self.prev_roads[0])

        #this will shift it to the side so the roads arent overlapping
        self_road_offset = self.get_road_offset(self.num_lanes)
        prev_road_offset = self.get_road_offset(prev_road.num_lanes)

        prev_road_direction = prev_road.direction

        #offset for length of road
        self.start_x = abs(prev_road.dirc[0]) * (prev_road.start_x + (prev_road.dirc[0] * (prev_road.length + abs(self_road_offset))))
        self.start_y = abs(prev_road.dirc[1]) * (prev_road.start_y + (prev_road.dirc[1] * (prev_road.length + abs(self_road_offset))))

        #offset for width of road
        if self.direction == (prev_road_direction - 1) % 4 or self.direction == (prev_road_direction + 1) % 4:
            self.start_x = (abs(prev_road.dirc[0]) * self.start_x) + abs(prev_road.dirc[1]) * (prev_road.start_x - (self.dirc[0] * prev_road_offset))
            self.start_y = (abs(prev_road.dirc[1]) * self.start_y) + abs(prev_road.dirc[0]) * (prev_road.start_y - (self.dirc[1] * prev_road_offset))
        elif self.direction == prev_road_direction:
            self.start_x = (abs(prev_road.dirc[0]) * self.start_x) + (abs(prev_road.dirc[1]) * prev_road.start_x)
            self.start_y = (abs(prev_road.dirc[1]) * self.start_y) + (abs(prev_road.dirc[0]) * prev_road.start_y)
        else:
            raise Exception('Cant have roads pointing at eachother')

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
        global num_cars

        self.id = num_cars
        num_cars += 1

        self.car_length = car_length
        self.car_width = car_width
        self.car_class = classType
        self.road_tag = road_tag
        #first value is current, second is new
        self.lane_num = [lane_num, lane_num]
        self.direction = self.get_lane().direction
        self.dirc = directions[self.direction]
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
        #how much space they're willing to have behind when changing lanes
        self.courage = 5

        self.draw_car()

    #always reading and writing opposites
    #if one isnt written they should be the same
    def read_speed(self, own = True):
        if tick:
            if not own:
                return self.speed[1]
            else:
                return self.speed[0]
        else:
            if not own:
                return self.speed[0]
            else:
                return self.speed[1]

    def write_speed(self, speed):
        self.has_speed_changed = True
        if tick:
            self.speed[0] = speed
        else:
            self.speed[1] = speed

    def update_speed(self):
        if tick:
            self.speed[1] = self.speed[0]
        else:
            self.speed[0] = self.speed[1]

    def read_lane_num(self, own = True):
        if tick:
            if not own:
                return self.lane_num[1]
            else:
                return self.lane_num[0]
        else:
            if not own:
                return self.lane_num[0]
            else:
                return self.lane_num[1]

    def write_lane_num(self, lane_num):
        self.has_lane_changed = True
        if tick:
            self.lane_num[0] = lane_num
        else:
            self.lane_num[1] = lane_num

    def update_lane_num(self):
        if tick:
            self.lane_num[1] = self.lane_num[0]
        else:
            self.lane_num[0] = self.lane_num[1]

    def read_distance_travelled(self, own = True):
        if tick:
            if not own:
                return self.distance_travelled[1]
            else:
                return self.distance_travelled[0]
        else:
            if not own:
                return self.distance_travelled[0]
            else:
                return self.distance_travelled[1]

    def write_distance_travelled(self, dist):
        self.has_dist_changed = True
        if tick:
            self.distance_travelled[0] = dist
        else:
            self.distance_travelled[1] = dist

    def update_distance_travelled(self):
        if tick:
            self.distance_travelled[1] = self.distance_travelled[0]
        else:
            self.distance_travelled[0] = self.distance_travelled[1]

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
        self.draw_start_point_x = self.get_lane().start_point_x + (self.dirc[0] * self.read_distance_travelled()) - (self.dirc[1] * (self.car_width / 2))
        self.draw_start_point_y = self.get_lane().start_point_y + (self.dirc[1] * self.read_distance_travelled()) - (self.dirc[0] * (self.car_width / 2))
        self.draw_end_point_x = self.draw_start_point_x + (self.dirc[0] * self.car_length) + (self.dirc[1] * self.car_width)
        self.draw_end_point_y = self.draw_start_point_y + (self.dirc[1] * self.car_length) + (self.dirc[0] * self.car_width)

        self.rect = canvas.create_rectangle(
            (self.draw_start_point_x, self.draw_start_point_y, self.draw_end_point_x, self.draw_end_point_y),
            width=1, outline='black', fill="blue", tags=self.road_tag)

        if show_nose:
            self.nose = canvas.create_rectangle(
                (self.draw_end_point_x, self.draw_end_point_y, self.draw_end_point_x + 3, self.draw_end_point_y + 3),
                width=1, outline='black', fill="green", tags=self.road_tag)

    def move(self):
        #tells vars whether to update
        self.has_speed_changed = False
        self.has_lane_changed = False
        self.has_dist_changed = False

        #move
        canvas.move(self.rect, self.speed_xy[0], self.speed_xy[1])
        if show_nose:
            canvas.move(self.nose, self.speed_xy[0], self.speed_xy[1])
        #putting own to false is a hack because i cant figure out the logic properly
        self.write_distance_travelled(self.read_distance_travelled(own = False) + self.read_speed())

        #other things
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
        #if critical
        change_lane_to = self.tend_change_lanes()
        if change_lane_to is not False:
            if self.can_change_lanes(change_lane_to):
                self.change_lanes(change_lane_to)
            #else:
            #   decelerate
        #else:
        self.accelerate()
        if self.read_speed() > self.max_speed:
            self.write_speed(self.max_speed)

        if not self.has_speed_changed:
            self.update_speed()
        if not self.has_lane_changed:
            self.update_lane_num()
        if not self.has_dist_changed:
            self.update_distance_travelled()

    def is_critical(self):
        #random atm
        return tick

    #working returns lane it wants to change to or False
    def tend_change_lanes(self):
        #should check dist to car infront in next lane, if > current lane return true
        #print '------------my lane'
        car_infront = self.get_lane_car_infront(self.read_lane_num())

        #If no cars infront dont want to change
        if car_infront == None:
            return False

        #look at lanes on either side
        for i in [self.read_lane_num() - 1, self.read_lane_num() + 1]:
            to_lane = None
            to_lane_dist = 0
            #dont look at own lane or lanes going in opposite direction
            if i >= 0 and i < self.get_road().num_lanes and self.get_road().lanes[i].direction == self.direction:
                #get closest car infront in next lane

                side_car_infront = self.get_lane_car_infront(i)
                if side_car_infront != None:
                    #if side_cat_infront is ahead of car_infront and remember that lane and compare it to previous
                    if side_car_infront.read_distance_travelled() > car_infront.read_distance_travelled()\
                            and side_car_infront.read_distance_travelled() > to_lane_dist:
                        to_lane = i
                        to_lane_dist = side_car_infront.read_distance_travelled()
                #there is a car infront but not to the side
                else:
                    return i
            if to_lane != None:
                return to_lane
        return False

    def can_change_lanes(self, lane):
        side_car_behind = self.get_lane_car_beside(lane)

        #Need to adjust to make more sense
        #
        #
        #
        if side_car_behind is None:
            return True
        if side_car_behind.read_distance_travelled() - self.courage > self.read_distance_travelled():
            return True

        return False

    #need algorithm for this
    def accelerate(self):

        #warning, dist can be negative
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

    #working
    def get_distance_to_next_intersection(self):
        return self.get_road().length - self.read_distance_travelled()

    def change_lanes(self, lane):
        self.write_lane_num(lane)

        #redraw car in other lane
        canvas.delete(self.rect)
        if show_nose:
            canvas.delete(self.nose)
        self.draw_car()

    def get_lane_car_beside(self, lane):
        # gets car beside so its properties can be checked
        car_beside = None
        closest_car_dist = 10000

        #
        #  cars is global list of cars
        #
        # Needs to take into account  road ahead and behind for edge cases
        # Maybe just make it so cant change close to end of road
        #
        #
        for car in cars:
            # same road, not self, in right lame, ahead of you, closer than current closest
            if car.road_tag == self.road_tag \
                    and car.id != self.id \
                    and car.read_lane_num() == lane \
                    and car.read_distance_travelled() < self.read_distance_travelled() + car_length \
                    and car.read_distance_travelled() < closest_car_dist:
                closest_car_dist = car.read_distance_travelled()
                car_beside = car
        return car_beside

    #working
    def get_lane_car_infront(self, lane):
        #gets car infront so its properties can be checked
        car_infront = None
        closest_car_dist = 10000

        #cars is global list of cars
        for car in cars:
            #same road, not self, in right lame, ahead of you, closer than current closest
            if car.road_tag == self.road_tag \
                    and car.id != self.id\
                    and car.read_lane_num() == lane\
                    and car.read_distance_travelled() > self.read_distance_travelled()\
                    and car.read_distance_travelled() < closest_car_dist:
                closest_car_dist = car.read_distance_travelled()
                car_infront = car
        return car_infront

    def next_road(self):
        if eval(self.road_tag).lanes[self.read_lane_num()].isOncoming:
            next_road = eval(eval(self.road_tag).prev_roads[self.next_direction])
        else:
            next_road = eval(eval(self.road_tag).next_roads[self.next_direction])
        self.road_tag = next_road.road_tag
        self.write_distance_travelled(0)

        self.direction = next_road.lanes[self.read_lane_num()].direction
        self.dirc = directions[self.direction]

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
'''road1 = Road(400,200,200,0,'road1',2,10, is_2way=True)
road2 = Road(700,200,200,1,'road2',2,10, is_2way=True, prev_roads=['road1'])
road3 = Road(700,200,200,2,'road3',2,10, is_2way=True, prev_roads=['road2'])
road4 = Road(700,200,200,3,'road4',2,10, is_2way=True, prev_roads=['road3'])'''

'''road1 = Road(400,600,200,2,'road1',2,10, is_2way=True)
road2 = Road(700,200,200,3,'road2',2,10, is_2way=True, prev_roads=['road1'])
road3 = Road(700,200,200,0,'road3',2,10, is_2way=True, prev_roads=['road2'])
road4 = Road(700,200,200,1,'road4',2,10, is_2way=True, prev_roads=['road3'])'''

'''road4.add_next_road('road1')
road1.add_prev_road('road4')

cars.append(Car('private_car','road1',0, offset=0))
cars.append(Car('private_car','road1',1, offset=80))
cars.append(Car('private_car','road1',0, offset=40))'''

#testing road ending with 2 directions
'''road1 = Road(500,200,300,1,'road1',2,10, is_2way=True)
road2 = Road(None,None,300,2,'road2',2,10, is_2way=True, prev_roads=['road1'])
road3 = Road(800,200,300,0,'road3',2,10, is_2way=True, prev_roads=['road1'])

road2.add_next_road('road1')
road3.add_next_road('road1')
road1.add_prev_road('road2')
road1.add_prev_road('road3')

cars.append(Car('private_car','road1',0, offset=80))
cars.append(Car('private_car','road1',1, offset=50))'''

#cycling left works
road1 = Road(800,200,300,2,'road1',2,10, is_2way=True)
road2 = Road(None, None, 300, 2, 'road2', 2,10, is_2way=True, prev_roads=['road1'])
road3 = Road(None, None, 100, 1, 'road3', 2,10, is_2way=True, prev_roads=['road2'])
road4 = Road(None, None, 100, 1, 'road4', 2,10, is_2way=True, prev_roads=['road3'])
road5 = Road(None, None, 300, 0, 'road5', 2,10, is_2way=True, prev_roads=['road4'])
road6 = Road(None, None, 300, 0, 'road6', 2,10, is_2way=True, prev_roads=['road5'])
road7 = Road(None, None, 100, 3, 'road7', 2,10, is_2way=True, prev_roads=['road6'])
road8 = Road(None, None, 100, 3, 'road8', 2,10, is_2way=True, prev_roads=['road7'])
road8.add_next_road('road1')
road1.add_prev_road('road8')

cars.append(Car('private_car','road1',0, offset=80))
cars.append(Car('private_car','road2',1, offset=80))

#offsets not working for road cycling right
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

for t in range(1000):
    time.sleep(0.025)
    move_cars(cars)
    canvas.update()
    tick = not tick

root.mainloop()
