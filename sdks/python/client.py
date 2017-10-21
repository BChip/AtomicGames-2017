#!/usr/bin/python

import sys
import json
import random

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
