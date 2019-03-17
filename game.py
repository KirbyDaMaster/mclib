
import os
import re

from mclib.data_interface import RomInterface
from mclib.area import Area
from mclib.map import Dungeon
from mclib.cutscene import Cutscene
from mclib.docs import ITEM_ID_TO_NAME

class Game:
  def __init__(self, input_rom_path):
    self.input_rom_path = input_rom_path
    
    self.rom = RomInterface(self.input_rom_path)
    
    self.read()
  
  def read(self):
    self.areas = []
    for area_index in range(0x90):
      area = Area(area_index, self.rom)
      self.areas.append(area)
    
    self.dungeons = []
    for dungeon_index in range(7):
      dungeon = Dungeon(dungeon_index, self.rom)
      self.dungeons.append(dungeon)
  
  def print_item_locations(self):
    output = []
    for area in self.areas:
      #print("Area %02X:" % area.area_index)
      for room in area.rooms:
        if room is None:
          continue
        #print("On room %02X-%02X:" % (area.area_index, room.room_index))
        
        for tile_entity in room.tile_entities:
          if tile_entity.type in [2, 3]:
            # Small chest or big chest
            item_name = ITEM_ID_TO_NAME[tile_entity.item_id]
            output.append("Room %02X-%02X:   Chest at %08X gives item %02X (%02X) - %s" % (area.area_index, room.room_index, tile_entity.entity_ptr, tile_entity.item_id, tile_entity.unknown_2, item_name))
        
        for entity_list in room.entity_lists:
          for entity in entity_list.entities:
            if entity.type == 7 or (entity.type == 6 and entity.subtype in [0x69]):
              if entity.params != 0:
                cutscene = Cutscene(entity.params, self.rom)
                for command in cutscene.commands:
                  if command.type == 0x82:
                    item_id = command.arguments[0]
                    item_name = ITEM_ID_TO_NAME[item_id]
                    output.append("Room %02X-%02X: Command at %08X gives item %02X (??) - %s" % (area.area_index, room.room_index, command.command_ptr, item_id, item_name))
              if entity.subtype == 3: # Minish
                cutscene_ptr = self.rom.read_u32(0x08109D18 + (entity.unknown_4 & 0xFF)*4)
                cutscene = Cutscene(cutscene_ptr, self.rom)
                for command in cutscene.commands:
                  if command.type == 0x82:
                    item_id = command.arguments[0]
                    item_name = ITEM_ID_TO_NAME[item_id]
                    output.append("Room %02X-%02X: Command at %08X gives item %02X (??) - %s" % (area.area_index, room.room_index, command.command_ptr, item_id, item_name))
    
    with open("item_locations.txt", "w") as f:
      for line in output:
        f.write(line + "\n")
