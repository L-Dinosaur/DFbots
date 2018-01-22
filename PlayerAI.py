from PythonClientAPI.Game import PointUtils
from PythonClientAPI.Game.Entities import FriendlyUnit, EnemyUnit, Tile
from PythonClientAPI.Game.Enums import Direction, MoveType, MoveResult
from PythonClientAPI.Game.World import World

import queue
import sys
import time
import heapq
class PlayerAI:

    def __init__(self):
        """
        Any instantiation code goes here
        """
        self.phase='early'
        self.potential_nest_set = None
        self.q = None
        self.cluster_allowed = 3
        self.our_depth_map = None
        self.enemy_depth_map = None
        self.potential_nest_dict = None
        self.territory = None

    def do_move(self, world, friendly_units, enemy_units):
        """
        This method will get called every turn.
        
        :param world: World object reflecting current game state
        :param friendly_units: list of FriendlyUnit objects
        :param enemy_units: list of EnemyUnit objects
        """
        # Fly away to freedom, daring fireflies
        # Build thou nests
        # Grow, become stronger
        # Take over the world


        # neutral_tiles = world.get_friendly_nest_positions()
        # print (neutral_tiles)
        # print (world.get_tiles_around(neutral_tiles[0].position))
        if self.potential_nest_set is None:
            self.q = queue.Queue()
            self.potential_nest_set = set()
            self.find_good_nest_location(world)
            self.potential_nest_location(world)
            self.potential_nest_dict = {}
            self.build_potential_nest_dict(world)
        # print(len(self.potential_nest_set))
        # print(len(self.potential_nest_dict))
        self.potential_nest_set = self.check_set_valid(world)
        self.potential_nest_dict = self.check_dict_valid(world)
        # print(len(self.potential_nest_set))
        # print(len(self.potential_nest_dict))


        f1 = open('C:\\Users\haodi\l_data\left_nests.csv', 'a')
        f2 = open('C:\\Users\haodi\l_data\have_nests.csv', 'a')
        f3 = open('C:\\Users\haodi\l_data\enemy_nests.csv', 'a')
        f4 = open('C:\\Users\haodi\l_data\have_tiles.csv', 'a')
        f5 = open('C:\\Users\haodi\l_data\enemy_tiles.csv', 'a')
        f6 = open('C:\\Users\haodi\l_data\have_fireflies.csv', 'a')
        f7 = open('C:\\Users\haodi\l_data\enemy_fireflies.csv', 'a')


        f1.write(str(len(self.potential_nest_set)) + ',')
        f2.write(str(len(world.get_friendly_nest_positions())) + ',')
        f3.write(str(len(world.get_enemy_nest_positions())) + ',')
        f4.write(str(len(world.get_friendly_tiles())) + ',')
        f5.write(str(len(world.get_enemy_tiles())) + ',')
        f6.write(str(len(world.get_position_to_friendly_dict().keys())) + ',')
        f7.write(str(len(world.get_position_to_enemy_dict().keys())) + ',')

        f1.close()
        f2.close()
        f3.close()
        f4.close()
        f5.close()
        f6.close()
        f7.close()

        # for i in range(19):
        #     for j in range (19):
        #         if (i,j) not in self.potential_nest_set:
        #             sys.stdout.write ('0 ')
        #         else:
        #             sys.stdout.write ('1 ')
        #     print ('')


        moved_unit = set()
        ###############################Attacker####################################################################

        ###############################Passive Defender####################################################################
        for unit in friendly_units:
            if unit in moved_unit:
                continue
            for key, value in world.get_tiles_around(unit.position).items():
                if value.is_enemy():
                    if world.get_closest_enemy_from(value.position,None).position == value.position:
                        world.move(unit, value.position)
                        moved_unit.add(unit)

        ###############################Harasser#######################################################################
        if len(friendly_units)> 15 and len(friendly_units)> len(enemy_units):
            if self.territory is None:
                self.build_territory_map(world)

            factor = 0.5
            num_attacker = max(int((len(friendly_units) - len(enemy_units))*factor),1)
            # Register (units):(distance from initial point)
            temp_dict = dict()
            for unit in friendly_units:
                temp_dict[unit] = self.our_depth_map[unit.position[0]][unit.position[1]]
            newDict = {key: value for key, value in temp_dict.items() if value in heapq.nlargest(num_attacker, temp_dict.values())}
            for k,v in newDict.items():
                if k in moved_unit:
                    continue
                # mask our own territory
                temp_set = set()
                temp_set2 = self.potential_nest_set.copy()
                for i in range(world.get_width()):
                    for j in range(world.get_height()):
                        if self.territory[i][j] == 0:
                            temp_set.add((i,j))
                        else:
                            if (i,j) in temp_set2:
                                temp_set2.remove((i,j))
                path = world.get_shortest_path(k.position,
                                               world.get_closest_capturable_tile_from(k.position,temp_set).position,
                                               temp_set2)
                if path: 
                    world.move(k, path[0]) 
                    moved_unit.add(k)               

        ###############################Constructor####################################################################
        # Construct a dictioncary of (position of NT):(distance)
        # temp_dict_ = dict()
        # for nt in world.get_neutral_tiles():
        #     temp_dict_[nt.position] = self.our_depth_map[nt[0]][nt[1]]
        if (len(self.potential_nest_dict)) > 0:
            nearest_nest = min(self.potential_nest_dict, key=self.potential_nest_dict.get)
            min_keys = [k for k in self.potential_nest_dict if self.potential_nest_dict[k] == self.potential_nest_dict[nearest_nest]]

            for nearest_nest in min_keys[:2]:
                nearest_unit = world.get_closest_friendly_from(nearest_nest,moved_unit)
                if nearest_unit is None:
                    break
                #print (nearest_unit.position)
                temp_dict = dict()
                for p in ((nearest_nest[0]+1,nearest_nest[1]),(nearest_nest[0]-1,nearest_nest[1]),(nearest_nest[0],nearest_nest[1]+1),(nearest_nest[0],nearest_nest[1]-1)):
                    if not world.is_within_bounds(p):
                        continue
                    if world.is_wall(p):
                        continue
                    temp_set = set([q.position for q in world.get_neutral_tiles()])
                    if p not in temp_set:
                        continue
                    temp_dict[p] = world.get_shortest_path_distance(p,nearest_unit.position)
                if len(temp_dict) > 0: 
                    nearest_tile = min(temp_dict, key=temp_dict.get)    
                    path = world.get_shortest_path(nearest_unit.position,
                                               nearest_tile,
                                               self.potential_nest_set)
                    if path: 
                        world.move(nearest_unit, path[0])
                        moved_unit.add(nearest_unit)



        ###############################Expansion####################################################################
        for unit in friendly_units:
            if unit in moved_unit:
                continue
            path = world.get_shortest_path(unit.position,
                                           world.get_closest_capturable_tile_from(unit.position, self.potential_nest_set).position,
                                           self.potential_nest_set)
            if path: world.move(unit, path[0])
        #print (time.time()-start_time)
    def potential_nest_location(self,world):

        neutral_tiles = world.get_neutral_tiles()
        friendly_nest_positions = world.get_friendly_nest_positions()
        w, h = world.get_width(),world.get_height()
        #print (w,h)
        nest_map = [[0 for i in range(w)] for j in range(h)] 

        for nt in neutral_tiles:
            nest_map[nt.position[0]][nt.position[1]] = 2
        for nt in self.potential_nest_set:
            nest_map[nt[0]][nt[1]] = 1
        for nest in friendly_nest_positions:
            self.our_depth_map = self.build_depth_map_from(nest,world)
            #self.q.put(nest)
            nest_map[nest[0]][nest[1]] = 1


            # Create Cluster
            cluster_list = [(nest[0],nest[1]),(nest[0]+1,nest[1]+1),(nest[0]+1,nest[1]-1),(nest[0]-1,nest[1]+1),(nest[0]-1,nest[1]-1)]
            for p in cluster_list:
                if nest_map[p[0]][p[1]] == 2:
                    stop_flag = False
                    x = p[0]
                    y = p[1]
                    for p_ in [(x+1,y+1),(x+1,y-1),(x-1,y+1),(x-1,y-1),(x+2,y),(x-2,y),(x,y+2),(x,y-2),(x+1,y+1),(x+1,y-1),(x-1,y-1),(x-1,y+1),(x+1,y),(x-1,y),(x,y-1),(x,y+1)]:
                        if p_ not in cluster_list and nest_map[p_[0]][p_[1]] == 1:
                            stop_flag = True
                            #print ('1233123213')
                        #print (p_,nest_map[p_[0]][p_[1]])
                    if stop_flag == False:
                        self.q.put(p)
                        nest_map[p[0]][p[1]] = 1  



        for nest in world.get_enemy_nest_positions():
            self.enemy_depth_map = self.build_depth_map_from(nest,world)
        for nest in self.potential_nest_set:
            #self.potential_nest_set.add(nest)
            self.q.put(nest)
            nest_map[nest[0]][nest[1]] = 1

        while (not self.q.empty()):
            current_nest_position = self.q.get()
            x = current_nest_position[0]
            y = current_nest_position[1]

            self.potential_nest_set.add(current_nest_position)

            nest_location_wo_cluster = [(x+2,y+1),(x+1,y-2),(x-1,y+2),(x-2,y-1),(x+1,y+2),(x+2,y-1),(x-2,y+1),(x-1,y-2),(x-3,y),(x+3,y),(x,y-3),(x,y+3)]
            for next_nest in nest_location_wo_cluster:
                if (next_nest[0] < 0) or (next_nest[0] >= w) or (next_nest[1] < 0) or (next_nest[1] >= h):
                    continue
                if nest_map[next_nest[0]][next_nest[1]] == 2:
                    if self.wont_form_cluster(next_nest,nest_map,w,h,world):
                        self.potential_nest_set.add(next_nest)
                        self.q.put(next_nest)
                        nest_map[next_nest[0]][next_nest[1]] = 1 
        return
    
    def build_potential_nest_dict(self,world):
        #print (self.potential_nest_set)
        for p in self.potential_nest_set:
            self.potential_nest_dict[p] = self.our_depth_map[p[0]][p[1]]

    def wont_form_cluster(self,nest,nest_map,w,h,world):
        x = nest[0]
        y = nest[1]
        #print (x,y)
        check_position = [(x+1,y+1),(x+1,y-1),(x-1,y+1),(x-1,y-1),(x+2,y),(x-2,y),(x,y+2),(x,y-2),(x+1,y+1),(x+1,y-1),(x-1,y-1),(x-1,y+1),(x+1,y),(x-1,y),(x,y-1),(x,y+1)]  
        for check in check_position:
            if (check[0] < 0) or (check[0] >= w) or (check[1] < 0) or (check[1] >= h):
                continue
            if world.is_wall(check):
                continue
            if nest_map[check[0]][check[1]] == 1:
                return False
        return True

    def check_set_valid(self,world):
        nt_position_list = set()
        for nt in world.get_neutral_tiles():
            nt_position_list.add(nt.position)

        temp_set = self.potential_nest_set.copy()
        for ns in self.potential_nest_set:
            if ns not in nt_position_list:
                temp_set.remove(ns)
        return temp_set

    def check_dict_valid(self,world):
        nt_position_list = set()
        for nt in world.get_neutral_tiles():
            nt_position_list.add(nt.position)

        temp_dict = self.potential_nest_dict.copy()
        for key, value in self.potential_nest_dict.items():
            if key not in nt_position_list:
                temp_dict.pop(key, None)
        return temp_dict
    def find_good_nest_location(self,world):
        w, h = world.get_width(),world.get_height()
        nest_map = [[0 for i in range(w)] for j in range(h)] 

        # 0 ---
        # 1 --- neutral tiles
        # 3 --- part of nests 
        for nt in world.get_neutral_tiles():
            nest_map[nt.position[0]][nt.position[1]] = 1
        for nest in world.get_friendly_nest_positions():
            nest_map[nt.position[0]][nt.position[1]] = 1
        for x in range(1,w-1):
            for y in range(1,h-1):
                if nest_map[x][y] != 1:
                    continue

                wall_flag = False
                cluster_flag = False
                for point in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
                    # check if wall exists
                    if world.is_wall(point):
                        wall_flag = True
                    # check if overlap with other 
                    elif nest_map[point[0]][point[1]] == 3:
                        cluster_flag = True
                        break
                if cluster_flag is False and wall_flag is True:
                    self.potential_nest_set.add((x,y))
                    for point in ((x+1,y),(x-1,y),(x,y+1),(x,y-1),(x,y)):
                        nest_map[point[0]][point[1]] = 3

    def build_depth_map_from(self,position,world):
        nest_map = [[0 for i in range(world.get_width())] for j in range(world.get_height())] 
        nest_map[position[0]][position[1]] = 0
        for i in range(world.get_width()):
            for j in range(world.get_height()):
                nest_map[i][j] = world.get_shortest_path_distance(position,(i,j))
        return nest_map

    # 0 - our territory
    # 1 - enemy territory    
    def build_territory_map(self,world):
        w = world.get_width()
        h = world.get_height()
        self.territory = [[0 for i in range(w)] for j in range(h)]
        for i in range(w):
            for j in range(h):
                if self.our_depth_map[i][j]>self.enemy_depth_map[i][j]:
                    self.territory[i][j] = 1
                    sys.stdout.write('1')
                else:
                    sys.stdout.write('0') 
            print ('')        


                    
        
