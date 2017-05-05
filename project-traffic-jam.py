# -*- coding: utf-8 -*-
"""
Created on Sun Apr 30 20:25:02 2017

@author: Cora
"""

import Tkinter as tk
import time
import math

Main_Road_Width= 400
Main_Road_Height = 400



root=tk.Tk()
root.title("Traffic Congestion Simulation")
canvas = tk.Canvas(root, width=Main_Road_Width, height=Main_Road_Height, bg="#FFFFFF")
canvas.pack()

class Lane():
    def __init__(self,start_x,start_y,lane_length,lane_width, road_tag, num_lanes, lane_num):
        self.tags = road_tag
        #Lanes are given a number so cars can change lanes just by counting up or down
        #When a car decides what lane it wants to be in a searches by road tag then filters for lane_num == desired_lane_num
        #road should have #lanes
        self.num_lanes = num_lanes
        self.lane_num = lane_num
        self.draw_start_point_x = start_x 
        self.draw_start_point_y = start_y - lane_width/2
        self.draw_end_point_x = start_x + lane_length
        self.draw_end_point_y = start_y + lane_width/2
        canvas.create_rectangle(
                (self.draw_start_point_x,self.draw_start_point_y,self.draw_end_point_x,self.draw_end_point_y),
                width=4,outline='black',fill="gray",tags=self.tags)
        
        self.start_point_x = start_x 
        self.start_point_y = start_y
        #end points may need to vary based on if lane is horizontal or vertical
        self.end_point_x = start_x + lane_length
        self.end_point_y = start_y
        
        self.speed_limit = 13.98/8.0
        self.to = [] # Directed graph neighbors
        self.car_agents = []

        #next road for car to join
        self.next_road = "tag of next road (lane number is inherited)"
        
    def get_lane_start_and_end(self):
        return self.start_point_x,self.start_point_y, self.end_point_x,self.end_point_y
    
    def get_lane_start(self):
        return self.start_point_x, self.start_point_y
    def get_lane_end(self):
        return self.end_point_x,self.end_point_y

    #to calculate where on road car is
    def get_euclidean_length(self):
        return "length"
    
    #def get_car_agents(self, lane_tag):
        #distance = 0
       # self.car_agents.sort(key=lambda car: car.E)
       # for car in canvas.find_withtag(lane_tag):
           # i = 
           # car_Eu_distance = car.get_Euclidian_distance(lane_tag)
           # if car_Eu_distance 
            

        

#class Road():
    #def __init__(lane_data):
        
        
        

class Car():
    def __init__(self,start_x,start_y,classType,road_tag, lane_num):
        self.car_length = 30
        self.car_width = 20
        self.car_class= classType
        self.tags = road_tag
        self.lane_num = lane_num
        #initial should be determined by lane (so inherits direction)
        self.speed = 3,0
        
        self.start_point_x = start_x
        self.start_point_y = start_y
        self.end_point_x = start_x + self.car_length
        self.end_point_y = start_y

        #Change to use trig to determine based on speed (as it gives direction)
        #Edit: cant do that- rectangles cant be diagonal
        self.draw_start_point_x = self.start_point_x
        self.draw_start_point_y = self.start_point_y - self.car_width / 2

        self.Eu_distance=0
        
    def get_car_start_and_end_point(self):
        return self.start_point_x, self.start_point_y, self.end_point_x, self.end_point_y
    def get_car_start(self):
        return self.start_point_x, self.start_point_y
    def get_car_end(self):
        return self.end_point_x, self.end_point_y

    #draw vertical or horizontal based on direction
    #needs to account for left vs right and up vs down
    def draw_car(self):
        #car moving left
        if self.speed[0] < 0:
            draw_end_point_x = self.start_x - self.car_length
            draw_end_point_y = self.start_y + self.car_width / 2
            self.rect = canvas.create_rectangle(
                (self.draw_start_point_x, self.draw_start_point_y, draw_end_point_x, draw_end_point_y),
                width=1, outline='black', fill="blue", tags=self.tags)
        #car moving right
        elif self.speed[0] > 0:
            draw_end_point_x = self.start_x + self.car_length
            draw_end_point_y = self.start_y + self.car_width / 2
            self.rect = canvas.create_rectangle(
                (self.draw_start_point_x, self.draw_start_point_y, draw_end_point_x, draw_end_point_y),
                width=1, outline='black', fill="blue", tags=self.tags)
        #for vertical just swap x and y when drawing
        #car moving down
        elif self.speed[1] < 0:
            draw_end_point_x = self.start_x + self.car_length
            draw_end_point_y = self.start_y + self.car_width / 2
            self.rect = canvas.create_rectangle(
                (self.draw_start_point_y, self.draw_start_point_x, draw_end_point_y, draw_end_point_x),
                width=1, outline='black', fill="blue", tags=self.tags)

        #default to car moving up
        else:
            draw_end_point_x = self.start_x - self.car_length
            draw_end_point_y = self.start_y + self.car_width / 2
            self.rect = canvas.create_rectangle(
                (self.draw_start_point_y, self.draw_start_point_x, draw_end_point_y, draw_end_point_x),
                width=1, outline='black', fill="blue", tags=self.tags)




    def move(self):
        canvas.move(self.rect, self.speed[0], self.speed[1])
    
    def set_speed(self,speed_x,speed_y):
        self.speed = speed_x, speed_y

    #Change speed based on neighbours
    def update_speed(self):
        self.speed = self.speed

    #Change lane if want to
    def change_lane(self):
        self.tags = self.tags
        self.lane_num += 1
        
    def get_Euclidian_distance(self, lane_tag):
        current_lane = canvas.find_withtag(lane_tag)
        lane_start_x, lane_start_y = current_lane.get_lane_start()
        Eu_distance = math.hypot((self.start_point_x - lane_start_x), (self.start_point_y - lane_start_y))
        self.Eu_distance = Eu_distance
        return Eu_distance
    
    def get_relative_Euclidian_distance(self, lane_tag):
        current_lane = canvas.find_withtag(lane_tag)
        lane_start_x, lane_start_y = current_lane.get_lane_start()
        relative_Eu_distance = math.hypot(0, (self.start_point_y - lane_start_y))
        
        return relative_Eu_distance

    #update road tag to next one
    def next_road(self):
        #condition needs to be fixed, but thats the idea
        if self.get_Euclidian_distance(self.tags) == canvas.gettags(self.tags).length:
            self.tags = canvas.gettags(self.tags).next_road
            #euclidean dist = 0
            #change speed to new road speed

class Bus(Car):
    def __init__(self,start_x,start_y,classType,lane_tag):
        if(classType == 'Bus'):
            self.car_length = 50
            self.car_width = 20
            self.car_class= classType
            self.tags = lane_tag
            self.speed = 2,0
            
            self.draw_start_point_x = start_x
            self.draw_start_point_y = start_y - self.car_width/2
            self.draw_end_point_x = start_x + self.car_length
            self.draw_end_point_y = start_y + self.car_width/2
            self.rect = canvas.create_rectangle(
                (self.draw_start_point_x,self.draw_start_point_y,self.draw_end_point_x,self.draw_end_point_y),
                width=1,outline='black',fill="green",tags=self.tags)
        
            
        
# make roads
lane1_length = 1000
lane1_width = 40
lane1_start_x = 0
lane1_start_y = 80
lane1_tags = 'road_main'
lane1_num_lanes = 1
lane1_lane_num = 0
lane1 = Lane(lane1_start_x,lane1_start_y,lane1_length,lane1_width, lane1_tags, lane1_num_lanes, lane1_lane_num)
start_x,start_y,end_x,end_y = lane1.get_lane_start_and_end()

#what's this?
lane2_length = 40
lane2_width = 80
lane2_start_x = 50
lane2_start_y = 80

lane2 = Lane(lane2_start_x,lane2_start_y,lane2_length,lane2_width, lane1_tags)

# make cars
private_car_start_x = 10
private_car_start_y = 90
private_car_lane_tags = 'road_main'
private_car_lane_num = 0
private_car_1=Car(private_car_start_x,private_car_start_y,'private_car',private_car_lane_tags, private_car_lane_num)
private_car_2=Car(start_x,start_y,'private_car',private_car_lane_tags, private_car_lane_num)

# make bus
Bus_start_x = 10
Bus_start_y = 90
Bus_lane_tags = 'lane_1'
Bus_1=Bus(Bus_start_x,Bus_start_y, 'Bus',Bus_lane_tags)
Bus_2=Bus(start_x,start_y, 'Bus',Bus_lane_tags)

private_car_1.set_speed(5,1)
Bus_1.set_speed(3,2)

for t in range(300):
    time.sleep(0.025)
    private_car_1.move()
    private_car_2.move()
    Bus_1.move()
    Bus_2.move()
    canvas.update()


root.mainloop()
