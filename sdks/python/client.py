#!/usr/bin/python

import sys
import json
import random
from collections import deque

if (sys.version_info > (3, 0)):
    print("Python 3.X detected")
    import socketserver as ss
else:
    print("Python 2.X detected")
    import SocketServer as ss


class NetworkHandler(ss.StreamRequestHandler):
    def handle(self):
        game = Game()

        while True:
            data = self.rfile.readline().decode() # reads until '\n' encountered
            json_data = json.loads(str(data))
            # uncomment the following line to see pretty-printed data
            # print(json.dumps(json_data, indent=4, sort_keys=True))
            # response = game.get_random_move(json_data).encode()
            response = game.gameResponse(json_data).encode()
            self.wfile.write(response)

class Game:
    def __init__(self):
        self.units = {} # set of unique unit ids
        self.tiles = {}
        self.dir = {}
        self.resourceCords = set()
        self.first = True
        self.discoveryUnits = []
        self.command = {"commands": []}

    def gameResponse(self, json_data):
        self.updateUnits(json_data)
        self.updateTiles(json_data)

        print self.resourceCords
        if self.first:
            response = self.firstMove()
        self.checkDiscoveryIsIdle()
        response = json.dumps(self.command, separators=(',',':')) + '\n'
        return response

    def firstMove(self):
        units = tuple(self.units.keys())
        self.discoveryUnits = [units[1], units[2], units[3], units[4]]
        self.units[units[1]].dir = "N"
        self.units[units[2]].dir = "E"
        self.units[units[3]].dir = "S"
        self.units[units[4]].dir = "W"
        self.command['commands'].append({"command": "MOVE", "unit": self.discoveryUnits[0], "dir": 'N'})
        self.command['commands'].append({"command": "MOVE", "unit": self.discoveryUnits[1], "dir": 'E'})
        self.command['commands'].append({"command": "MOVE", "unit": self.discoveryUnits[2], "dir": 'S'})
        self.command['commands'].append({"command": "MOVE", "unit": self.discoveryUnits[3], "dir": 'W'})

    def checkDiscoveryIsIdle(self):
        for unit in self.discoveryUnits:
            if self.units[unit].status == "idle":
                if self.units[unit].dir == 'N':
                    self.command['commands'].append({"command": "MOVE", "unit":unit, "dir": "E"})
                elif self.units[unit].dir == 'E':
                    self.command['commands'].append({"command": "MOVE", "unit":unit, "dir": "S"})
                elif self.units[unit].dir == 'S':
                    self.command['commands'].append({"command": "MOVE", "unit":unit, "dir": "W"})
                else:
                    self.command['commands'].append({"command": "MOVE", "unit":unit, "dir": "N"})


    def updateUnits(self, json_data):
        for unit in json_data['unit_updates']:
            id = unit['id']
            player_id = unit['player_id']
            x = unit['x']
            y = unit['y']
            unit_type = unit['type']
            status = unit['status']
            health = unit ['health']
            try:
                resources = unit['resource']
            except:
                resources = None
            try:
                can_attack = unit['can_attack']
            except:
                can_attack = None
            self.units[id] = Unit(id, player_id, x, y, unit_type, status, health, resources, can_attack)

    def updateTiles(self, json_data):
        for tile in json_data['tile_updates']:
            visible = tile['visible']
            x = tile['x']
            y = tile['y']
            try:
                blocked = tile['blocked']
            except:
                blocked = True
            try:
                resources = tile['resources']
            except:
                resources = None
            if resources:
                self.resourceCords.add((x,y))
            else:
                try:
                    self.resourceCords.remove((x,y))
                except:
                    pass
            self.tiles[(x,y)] = Tile(visible, x, y, blocked, resources)

    def moveUnits(self):
        for unit in self.units.values():
            if unit.player_id==my_id and unit.unit_type=='worker' and unit.status=='idle':
                # head home by default
                command = {"commands": [{"command": move, "unit": unit, "dir": self.get_direction(unit.x, unit.y, 0, 0)}]}

                if unit.resources==0:
                    try:
                        coord = resourceCords.pop()
                        command = {"commands": [{"command": move, "unit": unit, "dir": self.get_direction(unit.x, unit.y, coord)}]}
                        resourceCords.add(coord)
                    catch:
                        command = {"commands": [{"command": move, "unit": unit, "dir": self.explore(unit.x, unit.y)}]}

    def get_direction(x0, y0, x1, y1):
        if (x0,y0,x1,y1) in dir.keys():
            return dir[(x0,y0,x1,y1)]

        self.bfs(x1, y1)
        return dir[(x0,y0,x1,y1)]

    def bfs(x0, y0):
        q = deque([])
        dir[(x0, y0, x0, y0)] = 'X'
        q.append((x0,y0))

        while len(q)>0:
            x, y = q.popleft()

            # north
            if not (x,y-1,x0,y0) in dir.keys() and (x,y-1) in tiles.keys() and not tiles[(x,y-1)].blocked:
                dir[(x,y-1,x0,y0)] = 'S'
                q.append((x,y-1))
            # south
            if not (x,y+1,x0,y0) in dir.keys() and (x,y+1) in tiles.keys() and not tiles[(x,y+1)].blocked:
                dir[(x,y+1,x0,y0)] = 'N'
                q.append((x,y+1))
            # east
            if not (x+1,y,x0,y0) in dir.keys() and (x+1,y) in tiles.keys() and not tiles[(x+1,y)].blocked:
                dir[(x,y+1,x0,y0)] = 'W'
                q.append((x+1,y))
            # west
            if not (x-1,y,x0,y0) in dir.keys() and (x-1,y) in tiles.keys() and not tiles[(x-1,y)].blocked:
                dir[(x,y+1,x0,y0)] = 'E'
                q.append((x-1,y))


class Unit:
    def __init__(self, id, player_id, x, y, unit_type, status, health, resources, can_attack):
        self.id = id
        self.x = x
        self.y = y
        self.unit_type = unit_type
        self.status = status
        self.health = health
        self.resources = resources
        self.can_attack = can_attack
        self.dir = ""

class Tile:
    def __init__(self,visible,x,y,blocked,resources):
        self.x = x
        self.y = y
        self.blocked = blocked
        if resources == None:
            self.resources = resources
        else:
            self.resources = self.Resource(resources['id'], resources['type'], resources['total'], resources['value'])
        self.visible = visible

    class Resource:
        def __init__(self,id, type, total, value):
            self.id = id
            self.type = type
            self.total = total
            self.value = value

if __name__ == "__main__":
    port = int(sys.argv[1]) if (len(sys.argv) > 1 and sys.argv[1]) else 9090
    host = '127.0.0.1'

    server = ss.TCPServer((host, port), NetworkHandler)
    print("listening on {}:{}".format(host, port))
    server.serve_forever()
