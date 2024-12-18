class Boxtype:
    id: int
    l: int; w: int; h: int
    rot_l: bool; rot_w: bool; rot_h: bool
    weight: int
    volume: int

    def __init__(self, id, l, w, h, rot_l=True, rot_w=True, rot_h=True, weight=1):
        self.id = id
        self.l = l; self.w = w; self.h = h
        self.rot_l, self.rot_w, self.rot_h = rot_l, rot_w, rot_h
        self.weight = weight
        self.volume = l*w*h

# Items are pairs (Boxtype, quantity)
class Itemdict(dict):
    def __iadd__(self, other):
        for key in other:
            if key in self:
                self[key] += other[key]
            else:
                self[key] = other[key]
        return self

    def __isub__(self, other):
        for key in other:
            if key in self:
                self[key] -= other[key]
            else:
                self[key] = -other[key]
        return self
  
    def __le__(self, other):
        for key in other:
            if self[key] > other[key]:
                return False
        return True
            
    def __copy__(self):
        return Itemdict(self)

#An Aabb is cuboid+location
#Useful for representing free space cuboids and placed blocks
class Aabb:
    xmin: int; xmax: int
    ymin: int; ymax: int
    zmin: int; zmax: int
    l: int; w: int; h: int
    manhattan: int
    volume: int

    def __init__(self, xmin, xmax, ymin, ymax, zmin, zmax):
        self.xmin = xmin; self.xmax = xmax
        self.ymin = ymin; self.ymax = ymax
        self.zmin = zmin; self.zmax = zmax
        self.volume = (xmax-xmin)*(ymax-ymin)*(zmax-zmin)
        self.l = xmax-xmin; self.w = ymax-ymin; self.h = zmax-zmin
        self.manhattan = self.xmin + self.ymin + self.zmin
    
    # returns true if aabb is inside self
    def strict_intersects(self, aabb):
        return self.xmin < aabb.xmax and self.xmax > aabb.xmin and self.ymin < aabb.ymax and self.ymax > aabb.ymin and self.zmin < aabb.zmax and self.zmax > aabb.zmin
    
    # returns true if aabb intersects self
    def intersects(self, aabb):
        return self.xmin <= aabb.xmax and self.xmax >= aabb.xmin and self.ymin <= aabb.ymax and self.ymax >= aabb.ymin and self.zmin <= aabb.zmax and self.zmax >= aabb.zmin
    
    # returns a list of aabbs that are the result of substracting aabb from self    
    def subtract(self, aabb):
        sub = list()
        if aabb.xmax < self.xmax:
            sub.append(Aabb(aabb.xmax, self.xmax, self.ymin, self.ymax, self.zmin, self.zmax))
        if aabb.ymax < self.ymax:
            sub.append(Aabb(self.xmin, self.xmax, aabb.ymax, self.ymax, self.zmin, self.zmax))
        if aabb.zmax < self.zmax:
            sub.append(Aabb(self.xmin, self.xmax, self.ymin, self.ymax, aabb.zmax, self.zmax))
        if aabb.xmin > self.xmin:
            sub.append(Aabb(self.xmin, aabb.xmin, self.ymin, self.ymax, self.zmin, self.zmax))
        if aabb.ymin > self.ymin:
            sub.append(Aabb(self.xmin, self.xmax, self.ymin, aabb.ymin, self.zmin, self.zmax))
        if aabb.zmin > self.zmin:
            sub.append(Aabb(self.xmin, self.xmax, self.ymin, self.ymax, self.zmin, aabb.zmin))
        return sub
    
    def can_contain(self, aabb):
        return self.l >= aabb.l and self.w >= aabb.w and self.h >= aabb.h
    
    # aabb is contained in self
    def __ge__(self, aabb):
        return self.xmin <= aabb.xmin and self.xmax >= aabb.xmax and self.ymin <= aabb.ymin and self.ymax >= aabb.ymax and self.zmin <= aabb.zmin and self.zmax >= aabb.zmax
    
    def __str__(self):
        return "Aabb: xmin: " + str(self.xmin) + " xmax: " + str(self.xmax) + " ymin: " + str(self.ymin) + " ymax: " + str(self.ymax) + " zmin: " + str(self.zmin) + " zmax: " + str(self.zmax)


#An Aabb is cuboid+location
#Useful for representing free space cuboids and placed blocks
class Aabb:
    xmin: int; xmax: int
    ymin: int; ymax: int
    zmin: int; zmax: int
    l: int; w: int; h: int
    volume: int

    def __init__(self, xmin, xmax, ymin, ymax, zmin, zmax):
        self.xmin = xmin; self.xmax = xmax
        self.ymin = ymin; self.ymax = ymax
        self.zmin = zmin; self.zmax = zmax
        self.volume = (xmax-xmin)*(ymax-ymin)*(zmax-zmin)
        self.l = xmax-xmin; self.w = ymax-ymin; self.h = zmax-zmin
    
    # returns true if aabb is inside self
    def strict_intersects(self, aabb):
        return self.xmin < aabb.xmax and self.xmax > aabb.xmin and self.ymin < aabb.ymax and self.ymax > aabb.ymin and self.zmin < aabb.zmax and self.zmax > aabb.zmin
    
    # returns true if aabb intersects self
    def intersects(self, aabb):
        return self.xmin <= aabb.xmax and self.xmax >= aabb.xmin and self.ymin <= aabb.ymax and self.ymax >= aabb.ymin and self.zmin <= aabb.zmax and self.zmax >= aabb.zmin
       
    def can_contain(self, aabb):
        return self.l >= aabb.l and self.w >= aabb.w and self.h >= aabb.h
    
    # aabb is contained in self
    def __ge__(self, aabb):
        return self.xmin <= aabb.xmin and self.xmax >= aabb.xmax and self.ymin <= aabb.ymin and self.ymax >= aabb.ymax and self.zmin <= aabb.zmin and self.zmax >= aabb.zmax
    
    def __str__(self):
        return "Aabb: xmin: " + str(self.xmin) + " xmax: " + str(self.xmax) + " ymin: " + str(self.ymin) + " ymax: " + str(self.ymax) + " zmin: " + str(self.zmin) + " zmax: " + str(self.zmax)

class Space(Aabb):
    manhattan: int #the manhattan distance to the closest corner of the space to a block's corner
    corner_point: list() #the closest corner of the space to a block's corner

    #static variable
    filling = "origin" #the filling method used by the algorithm
    vertical_stability = True # boxes must be completly supported

    def __init__(self, xmin, xmax, ymin, ymax, zmin, zmax, block):
        super().__init__(xmin, xmax, ymin, ymax, zmin, zmax)
        self.container_block = block
        self.corner_point = [xmin, ymin, zmin]
        xdist = xmin; ydist = ymin; zdist = zmin
        if  Space.filling == "bottom-up": zdist = 1000*zmin

        #compute manhattan distance to the closest corner of the block
        if block.l-xmax < xmin and Space.filling != "origin":
            xdist = block.l-xmax
            self.corner_point[0] = xmax

        if block.w-ymax < ymin and Space.filling != "origin":
            ydist = block.w-ymax
            self.corner_point[1] = ymax

        if block.h-zmax < zmin and Space.filling == "free": 
            zdist = block.h-zmax
            self.corner_point[2] = zmax

        self.manhattan = xdist + ydist + zdist
        
    # returns a list of aabbs that are the result of substracting aabb from self    
    def subtract(self, aabb, container_block):
        sub = list()
        if aabb.xmax < self.xmax:
            sub.append(Space(aabb.xmax, self.xmax, self.ymin, self.ymax, self.zmin, self.zmax, container_block))
        if aabb.ymax < self.ymax:
            sub.append(Space(self.xmin, self.xmax, aabb.ymax, self.ymax, self.zmin, self.zmax, container_block))
        if aabb.zmax < self.zmax:
          if Space.vertical_stability==False:
            sub.append(Space(self.xmin, self.xmax, self.ymin, self.ymax, aabb.zmax, self.zmax, container_block))
          else:
            sub.append(Space(aabb.xmin, aabb.xmax, aabb.ymin, aabb.ymax, aabb.zmax, self.zmax, container_block))
        if aabb.xmin > self.xmin:
            sub.append(Space(self.xmin, aabb.xmin, self.ymin, self.ymax, self.zmin, self.zmax, container_block))
        if aabb.ymin > self.ymin:
            sub.append(Space(self.xmin, self.xmax, self.ymin, aabb.ymin, self.zmin, self.zmax, container_block))
        if aabb.zmin > self.zmin:
            sub.append(Space(self.xmin, self.xmax, self.ymin, self.ymax, self.zmin, aabb.zmin, container_block))
        return sub

    


    
#FreeSpaace represent the free space inside a block
#Consists of a list of free space aabbs (spaces)
class FreeSpace:
    spaces : list() # list of aabbs
    def __init__(self, aabb=None):
        self.spaces = list()
        if aabb is not None:
          self.spaces.append(aabb)

    def remove_nonmaximal_spaces(self, aabbs):
      #sort aabbs by volume
      aabbs.sort(key=lambda aabb: aabb.volume, reverse=True)

      for i in range(len(aabbs)):
        if i>=len(aabbs): break
        for j in range(i+1, len(aabbs)):   
          if j>=len(aabbs): break
          if aabbs[i] >= aabbs[j]:
              aabbs.remove(aabbs[j])
              j -= 1
          
    def crop(self, aabb, container_block):
        new_spaces = list()
        to_remove = list()
        for space in self.spaces:
            if space.intersects(aabb):                
                if space.strict_intersects(aabb):
                    sub = space.subtract(aabb, container_block)
                    for s in sub: new_spaces.append(s)
                else:
                    new_spaces.append(space)
                
                to_remove.append(space)

        for sp in to_remove: self.spaces.remove(sp)

        self.remove_nonmaximal_spaces(new_spaces)

        self.spaces.extend(new_spaces)

    #compute the free space closer to the origin (manhattan distance)
    def closest_space(self):
        min = 1000000; cspace=None
        for space in self.spaces:
            if space.manhattan < min: 
              min = space.manhattan
              cspace = space
        if cspace == None: return None
        else: return cspace


    #remove all spaces that cannot be filled by a boxtype
    def filter(self, items):
        to_remove = list()
        for space in self.spaces:
            remove = True
            for item in items:
                if items[item]>0 and space.l >= item.l and space.w >= item.w and space.h >= item.h:
                    remove = False
                    break
            if remove==True: to_remove.append(space)

        for sp in to_remove: self.spaces.remove(sp)

    def __str__(self):
        _str = ""
        for space in self.spaces:
          _str+= str(space) +"\n"
        return _str

from copy import copy
from types import NoneType

#A block is compund by a set of items(boxtype+quantity)
#The container is a block
class Block:
    l: int; w: int; h: int
    occupied_volume: int
    weight: int
    volume: int
    items: Itemdict() # Boxtype: int
    free_space: FreeSpace() # list of free spaces
    aabbs: list() # placed blocks
    tokens: list()

     # copy blocks and items
    def __copy__(self):
        return Block(copy_block=self) 

    def __init__(self, boxtype=None, rot=True, l=0, w=0, h=0, copy_block=None, items=None):

        if items is not None: #block of boxes
            self.l = l
            self.w = w
            self.h = h      
            self.volume = l*w*h
            self.weight = 0
            self.occupied_volume = 0
            for item in items:
              self.occupied_volume += item.volume*items[item]
              self.weight += item.weight*items[item]
            self.items = Itemdict()
            self.items += items

        elif copy_block is not None:
            # copy blocks and items
            self.l = copy_block.l
            self.w = copy_block.w
            self.h = copy_block.h
            self.weight = copy_block.weight
            self.occupied_volume = copy_block.occupied_volume
            self.volume = copy_block.volume
            self.items = Itemdict()
            self.items += copy_block.items
            self.tokens = copy_block.tokens
            #self.free_spaces
            #self.aabbs 

        elif boxtype is not None:
          if rot[0]=='w': self.l = boxtype.w
          elif rot[1]=='w': self.w = boxtype.w
          elif rot[2]=='w': self.h = boxtype.w

          if rot[0]=='l': self.l = boxtype.l
          elif rot[1]=='l': self.w = boxtype.l
          elif rot[2]=='l': self.h = boxtype.l        

          if rot[0]=='h': self.l = boxtype.h
          elif rot[1]=='h': self.w = boxtype.h
          elif rot[2]=='h': self.h = boxtype.h
          
          self.weight = boxtype.weight
          self.occupied_volume = boxtype.volume
          self.volume = boxtype.volume
          self.items = Itemdict()
          self.items[boxtype] = 1
          self.free_spaces = FreeSpace() # empty list of free spaces
          self.tokens = []

        else: 
          self.l = l; self.w = w; self.h = h
          self.occupied_volume = 0
          self.weight = 0
          self.items = Itemdict()
          self.volume = l*w*h
          self.aabbs = []
          self.free_space = FreeSpace(Space(0, self.l, 0, self.w, 0, self.h, self)) # all is free space

    def add_block(self, block, space):
        x,y,z = space.corner_point
        if x == space.xmax: x -= block.l
        if y == space.ymax: y -= block.w
        if z == space.zmax: z -= block.h

        self.aabbs.append(Aabb(x,x+block.l,y,y+block.w,z,z+block.h))
        self.occupied_volume += block.occupied_volume
        self.weight += block.weight
        self.items += block.items
        self.free_space.crop(Aabb(x, x+block.l, y, y+block.w, z, z+block.h), self) # remove the space occupied by the block


    #x:w, y:l, z:h
    def join(self, block, dim, min_fr=0.98):
        if dim=='x':
            l = self.l + block.l; w = max(self.w, block.w); h = max(self.h, block.h); volume = w*l*h
            if (self.occupied_volume + block.occupied_volume)/volume < min_fr: return False
            self.weight += block.weight
            self.occupied_volume += block.occupied_volume
            self.volume = volume
            self.items += block.items
        elif dim=='y':
            l = max(self.l, block.l); w = self.w + block.w; h = max(self.h, block.h); volume = w*l*h
            if (self.occupied_volume + block.occupied_volume)/volume < min_fr: return False
            self.weight += block.weight
            self.occupied_volume += block.occupied_volume
            self.volume = volume
            self.items += block.items
        elif dim=='z':
            l = max(self.l, block.l); w = max(self.w, block.w); h = self.h + block.h; volume = w*l*h
            if (self.occupied_volume + block.occupied_volume)/volume < min_fr: return False
            self.weight += block.weight
            self.occupied_volume += block.occupied_volume
            self.volume = volume
            self.items += block.items
        self.l = l; self.w = w; self.h = h

        return True

    def is_constructible(self, items):
        for item in self.items:
            if items[item] < self.items[item]:
                return False
        return True
    
    @staticmethod
    def generate_blocks(b1, b2, min_fr=0.98):
        a = copy(b1)
        if a.join(b2, 'x', min_fr): 
            yield a; a =  copy(b1)

        if a.join(b2, 'y', min_fr): 
            yield a; a =  copy(b1)

        if a.join(b2, 'z', min_fr): 
            yield a; 

    def occupied_volume_ratio(self):
        return self.occupied_volume/self.volume
    
    def __le__(self, other):
        return self.l <= other.l and self.w <= other.w and self.h <= other.h
      
    def __str__(self):
        return "Block: l: " + str(self.l) + " w: " + str(self.w) + " h: " + str(self.h) + " weight: " + str(self.weight) + " volume: " + str(self.volume) + " occupied_volume: " + str(self.occupied_volume) + " items: " + str(self.items) + " ratio:" + str(self.occupied_volume_ratio())

class BlockList(list):
    def __init__(self, items, type, cont=None, min_fr=0.98, max_bl=10000, *args):
        super().__init__(*args)
        if(type=="simple_blocks"):
            self.generate_simple_blocks(items)

        if(type=="general_blocks"):
            self.generate_general_blocks(items,cont, min_fr, max_bl)

    def generate_general_blocks(self,items,cont,min_fr=0.98, max_bl=10000):
        self.generate_simple_blocks(items)
                                   
        B = self
        P = B.copy()

        while len(B) < max_bl:
            N = list()
            for b1 in P:
                for b2 in B:
                    for new_block in Block.generate_blocks(b1, b2, min_fr):
                        if new_block.is_constructible(items) and new_block <= cont:
                            N.append(new_block)
                            if len(B) + len(N) >= max_bl: break

                    if len(B) + len(N) >= max_bl: break

                if len(B) + len(N) >= max_bl: break

            if len(N) == 0: break
            B.extend(N)
            P = N


    def generate_simple_blocks(self,items):
        #items is a dictionary of boxtype->number
        for item in items:
            self.append(Block(item,"lwh"))
            if item.rot_l ==True:
                self.append(Block(item,"whl"))
                self.append(Block(item,"hwl"))
            
            if item.rot_w ==True:
                self.append(Block(item,"lhw"))
                self.append(Block(item,"hlw"))

            if item.rot_h ==True: # trivial
                #self.append(Block(item,"lwh"))
                self.append(Block(item,"wlh"))


    def best(blocks, space, cont, eval_function, ctr_functions):
      best_block = None; best_eval = float("-inf")
      for block in blocks:
        # Check if all constraints are True for the current block
        if all(ctr(block, space, cont) for ctr in ctr_functions):   
          ev = eval_function(block, space, cont)
          if ev > best_eval:
            best_block = block
            best_eval = ev

      return best_block



    #remove blocks that cannot be constructed with the given items(boxtype->number)
    def remove_unconstructable(blocks, items):
        #cannot remove while iterating
        to_remove = list()
        for block in blocks:
            if not block.is_constructible(items):
                to_remove.append(block)
        for block in to_remove:
            blocks.remove(block)

    def __str__(self):
        _str = ""
        for block in self:
            _str+= str(block) + "\n"



