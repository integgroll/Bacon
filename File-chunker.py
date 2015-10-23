import pprint
import random
import sqlite3
import os
import errno
import math
import time
import sqlobject# import StringCol, SQLObject, ForeignKey, sqlhub, connectionforURI

#Yeah bro, let's open up a connection with our database...
sqlobject.sqlhub.processConnection = sqlobject.connectionForURI('sqlite:' + os.path.abspath('bacon.db'))

#Bacon Strips are commands that have been fed to the interpreter
# The commands are currently unset, but an individual Bacon shell can queue up many different commands. 
# This can be anything from adjusting the rate of communication, changing the point of communication, if the command has been run or not 
class BaconStrip(sqlobject.SQLObject):
  strip_id = sqlobject.StringCol() # Non database Unique Identifier mostly to ensure the session data passes correctly because yaknow UDP
  the_order = sqlobject.IntCol() # Obviously holds the order that this is supposed to go in 
  executed = sqlobject.TimeCol() # Tells you if the command has been executed
  command = sqlobject.StringCol() # 
#BaconChunks are the Files that are going to be uploaded, Essentially these are just pointers to the filename until it is actually time to do the transfer
# At that point they are then loaded into memory and then allowed to be transferred
# Uploads over this format take forever and take a TON of packets so it is best to try to keep them as small as possible.
# Trust me on this, we are talking 64 bytes per packet, If a file has to be split, oh god I feel sorry for everyone.
class BaconChunk(sqlobject.SQLObject):
  chunk_id = sqlobject.StringCol() # Non database Unique Identifier mostly to ensure session data is passed correctly because yaknow UDP
  filename = sqlobject.StringCol() # Filename of the data to transfer
#Not 100% sure that Bacon Bits are needed on the Server Side, they are on the client though I believe for Commands
#Bacon Bits are the tiny building blocks of things, they are what actually holds the individual blocks of files 
# Each BaconChunk can contain a number of BaconBits, which are the end all building block of transfer information
# This line is fake information that will actually help someone coding for this not at all but makes the code look better.
#class BaconBit(sqlobject.SQLObject):
#  chunk = sqlobject.ForeignKey('BaconChunk') # Foreign Key for the Chunk Database
#  the_order = sqlobject.IntCol() # Obviously hold the order that this stuff is supposed to go in
#  start_frame = sqlobject.IntCol() # Holds the start of the frame in reference to the file when in memory
#  end_frame = sqlobject.IntCol() # Holds the end of the frame in reference to the file when in memory
    
#Making Tables from my Schema
BaconStrip.createTable(ifNotExists=True)    
BaconChunk.createTable(ifNotExists=True)
#BaconBit.createTable(ifNotExists=True)   



files = {}

pp = pprint.PrettyPrinter(indent=4)

# The Structure for the "file" references are going to be as follows
# 16 bits that define a unique identifier for anything going on
# 16 bits that define the kind of transaction that is being generated
# 0000 0000 XXXX XXXX These bits reference the Length of the padding of the current frame It generally only appears on the last frame 
# 1000 0000 0000 0000 File Download
# 0100 0000 0000 0000 Command Download
# 0000 1000 0000 0000 Request size request response
# 0000 0100 0000 0000 File name (can and should be size requested)
# xxxx xxxx xxxx xxxx Doesn't matter yet just leaving spare space for shit
class FileManager:
  def __init__(self, filename , buffersize = 12):
    if os.path.exists(filename):
      self.chunk_size = buffersize
      self.filename = filename
      self.file_handler = None
      self.file_size = os.stat(filename).st_size
      self.number_of_chunks = math.ceil(self.file_size / float(self.chunk_size)) # Without the ugly remainder
      self.padding_size = self.chunk_size - (self.file_size % self.chunk_size)
      # At this point I will include the SUPER MEGA TACKY LOOKING DATABASE ADDITION CODE!!!!!
    else:
      raise AssertionError("File Does not Exist")
    return None

  # Reads a chunk of a file so that we can safely process things one at a time
  def read_chunk(self, chunk_number):
    chunk_data = self.raw_read_chunk(chunk_number)
    return  chunk_data + "0" * (self.chunk_size - len(chunk_data))
  
  # Read a chunk without any padding added. It is needed sometimes, however dumb it is.
  def raw_read_chunk(self, chunk_number):
    self.file_handler = open(self.filename)
    self.file_handler.seek(self.chunk_size * chunk_number)
    return self.file_handler.read(self.chunk_size)    

  def file_info(self):
    print "******** FILE INFO BLOCK ********"
    print "File Length:", self.file_size
    print "Chunk Size:", self.chunk_size
    print "Number of Chunks:", self.number_of_chunks
    print "Padding:", self.chunk_size - self.file_size % self.chunk_size
    print "******** FILE INFO BLOCK ********"
    
  def file_info_packer(self):
    print "Returns magic packet information"
    packed_data = ""
    return packed_data
#{ "variables":[],"data":[], "function":self.thursday}
class BaconFryer:
  def __init__(self):
    self.wednesday = "tuesday"
    self.menus= {"1":("Commands",{"1":("List",                  {"1":("Incomplete",self.show_incomplete_commands),
                                                                 "2":("Completed",self.show_complete_commands)}),
                                  "2":("Add",                   {"1":("List",self.command_loop),
                                                                 "2":("Add",self.file_loop)}),
                                  "3":("Delete",self.file_loop),
                                  "4":("Add",self.file_loop),}),
                 "2":("Files",{   "1":("Commands",self.command_loop),
                                  "2":("Files",self.file_loop),})
                }
    # I know the previous stuff looks horrendous, I think it actually looks better than 90% of other peoples menu driven programs,
    # Why you ask? Look at all the times I am not repeating myself and wasting bullshit time on menus and repeating the same gorram
    # code over and over again. 
    #
    # The menu and command drivers are what really drive all of this code in this section.  Combined with the messy ass menus list
    # that is above us we see a really great way to get menus done in a system like this without having to write the shit into every
    # gorram function that we write. The aditional bonus on this is that I get to run the functions after just asking a few pre-setup
    # questions that are always going to be the same overall.
    # Also, this needs a menu generator as well, which I am pretty sure I can create, but I think that will end up turned into its own
    # spunout module that I will pass on to others
    
  def menu_driver(self,menu=None):
    while True:
      if menu==None:
        menu=self.menus
      menu["99"]=("Quit",self.vegan) #Homage to Dave and SET of course, not the vegan part but the 99 part
      os.system("clear")
      for key in sorted(menu.keys()):
        print key+":" + menu[key][0]
      ans = raw_input("You are likely to be eaten by a grue")
      if ans == "99":
        break #Ugliest way in the world to do this or so I think.
      if type(menu[ans][1])==dict:
        if "variables" in menu[ans][1]:
          self.command_driver(menu[ans][1])
        else:
          self.menu_driver(menu.get(ans,[None,self.invalid])[1])
      else:
        menu.get(ans,[None,self.invalid])[1]()
  
  def command_driver(self,command_array):
    for i in range(len(command_array["variables"])):
      command_array["data"][i] = raw_input("Input a " + command_array["variables"][i] + ":")
    command_array.get("function",[None,self.invalid])(*command_array["data"])
  
  def vegan(self):
    pass
    
  def invalid(self):
    print "You were eaten by a grue"
  
  
  
  def show_complete_commands(self,):
    print "These are all of the Complete BaconStrips "
  
  def show_incomplete_commands(self,):
    print "These are all of the Incomplete BaconStrips "
  
  def tuesday(self,apples,oranges):
    print apples
    print oranges
        
  def command_loop(self):
    print "Yo Dog this is the command entry section"
    
  def file_loop(self):
    print "Yo Dog this is the file system, it does things and other things"

  def print_header(self):
    os.system("clear")
    print """#==========================================================#   
|                                                          |
|    BACON Control System: Fryer On!!!!!!!                 |
|                                                          |    
#==========================================================#"""
    time.sleep(2)

apples = FileManager("test.txt")
print apples.read_chunk(0)
print apples.read_chunk(14)
apples.file_info()

oranges = BaconFryer()
oranges.print_header()
oranges.menu_driver()
