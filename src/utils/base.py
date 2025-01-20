from copy import deepcopy


class Boxtype:
    """
    Represents a type of box for container loading problems.

    Attributes:
        id (int): Unique identifier for the box type.
        l (int): Length of the box.
        w (int): Width of the box.
        h (int): Height of the box.
        rot_l (bool): Indicates if the box can be rotated along its length. Default is True.
        rot_w (bool): Indicates if the box can be rotated along its width. Default is True.
        rot_h (bool): Indicates if the box can be rotated along its height. Default is True.
        weight (int): Weight of the box. Default is 1.
        volume (int): Volume of the box, calculated as l * w * h.
    """
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

class Itemdict(dict):
    """
    A dictionary subclass to manage pairs of (Boxtype, quantity) with additional functionality.

    Supports:
    - In-place addition (__iadd__) and subtraction (__isub__) of quantities for existing or new keys.
    - Comparison (__le__) to check if all quantities in the dictionary are less than or equal to another.
    - Copying (__copy__) for creating shallow copies.
    """

    def __iadd__(self, other):
        """
        Adds the quantities of another Itemdict to the current one in-place.
        If a key exists, its quantity is incremented; otherwise, it is added.

        Parameters:
            other (Itemdict): Another Itemdict to add.

        Returns:
            Itemdict: The updated dictionary.
        """
        for key in other:
            if not isinstance(other[key], int):
                raise ValueError("All quantities must be integers.")
            self[key] = self.get(key, 0) + other[key]
        return self

    def __isub__(self, other):
        """
        Subtracts the quantities of another Itemdict from the current one in-place.
        If a key exists, its quantity is decremented; otherwise, it is added with a negative value.

        Parameters:
            other (Itemdict): Another Itemdict to subtract.

        Returns:
            Itemdict: The updated dictionary.
        """
        for key in other:
            if not isinstance(other[key], int):
                raise ValueError("All quantities must be integers.")
            self[key] = self.get(key, 0) - other[key]
        return self

    def __le__(self, other):
        """
        Checks if all quantities in the current dictionary are less than or equal to those in another.

        Parameters:
            other (Itemdict): Another Itemdict to compare against.

        Returns:
            bool: True if all quantities are less than or equal to those in 'other', False otherwise.
        """
        for key in self:
            if self[key] > other.get(key, 0):
                return False
        return True

    def __copy__(self):
        """
        Creates a shallow copy of the current Itemdict.

        Returns:
            Itemdict: A new Itemdict instance with the same content.
        """
        return Itemdict(self)

    def __deepcopy__(self, memo):
        """
        Creates a deep copy of the current Itemdict.

        Parameters:
            memo (dict): A memoization dictionary for deep copies.

        Returns:
            Itemdict: A deep copy of the dictionary.
        """
        return Itemdict(deepcopy(dict(self), memo))



class Aabb:
    """
    Represents an Axis-Aligned Bounding Box (AABB), a cuboid with a location in 3D space.

    Attributes:
        xmin, xmax (int): Minimum and maximum x-coordinates.
        ymin, ymax (int): Minimum and maximum y-coordinates.
        zmin, zmax (int): Minimum and maximum z-coordinates.
        l, w, h (int): Dimensions (length, width, height) of the AABB.
        manhattan (int): Manhattan distance from the origin (xmin + ymin + zmin).
        volume (int): Volume of the cuboid, calculated as l * w * h.
    """

    def __init__(self, xmin: int, xmax: int, ymin: int, ymax: int, zmin: int, zmax: int):
        """
        Initializes an AABB with its coordinates.

        Parameters:
            xmin, xmax (int): Minimum and maximum x-coordinates.
            ymin, ymax (int): Minimum and maximum y-coordinates.
            zmin, zmax (int): Minimum and maximum z-coordinates.

        Raises:
            ValueError: If any maximum coordinate is less than its corresponding minimum.
        """
        if xmax <= xmin or ymax <= ymin or zmax <= zmin:
            raise ValueError("Maximum coordinates must be greater than minimum coordinates.")
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax
        self.zmin = zmin
        self.zmax = zmax
        self.l = xmax - xmin
        self.w = ymax - ymin
        self.h = zmax - zmin
        self.volume = self.l * self.w * self.h
        self.manhattan = xmin + ymin + zmin

    def strict_intersects(self, aabb: "Aabb") -> bool:
        """
        Checks if the given AABB strictly intersects with the current AABB.

        Parameters:
            aabb (Aabb): Another AABB to check for intersection.

        Returns:
            bool: True if the two AABBs strictly intersect, False otherwise.
        """
        return (
            self.xmin < aabb.xmax and self.xmax > aabb.xmin and
            self.ymin < aabb.ymax and self.ymax > aabb.ymin and
            self.zmin < aabb.zmax and self.zmax > aabb.zmin
        )

    def intersects(self, aabb: "Aabb") -> bool:
        """
        Checks if the given AABB intersects with or touches the current AABB.

        Parameters:
            aabb (Aabb): Another AABB to check for intersection.

        Returns:
            bool: True if the two AABBs intersect or touch, False otherwise.
        """
        return (
            self.xmin <= aabb.xmax and self.xmax >= aabb.xmin and
            self.ymin <= aabb.ymax and self.ymax >= aabb.ymin and
            self.zmin <= aabb.zmax and self.zmax >= aabb.zmin
        )

    def subtract(self, aabb: "Aabb") -> list:
        """
        Subtracts the given AABB from the current AABB and returns the resulting AABBs.

        Parameters:
            aabb (Aabb): The AABB to subtract.

        Returns:
            list: A list of AABBs that represent the remaining volume.
        """
        subtracted = []
        if aabb.xmax < self.xmax:
            subtracted.append(Aabb(aabb.xmax, self.xmax, self.ymin, self.ymax, self.zmin, self.zmax))
        if aabb.ymax < self.ymax:
            subtracted.append(Aabb(self.xmin, self.xmax, aabb.ymax, self.ymax, self.zmin, self.zmax))
        if aabb.zmax < self.zmax:
            subtracted.append(Aabb(self.xmin, self.xmax, self.ymin, self.ymax, aabb.zmax, self.zmax))
        if aabb.xmin > self.xmin:
            subtracted.append(Aabb(self.xmin, aabb.xmin, self.ymin, self.ymax, self.zmin, self.zmax))
        if aabb.ymin > self.ymin:
            subtracted.append(Aabb(self.xmin, self.xmax, self.ymin, aabb.ymin, self.zmin, self.zmax))
        if aabb.zmin > self.zmin:
            subtracted.append(Aabb(self.xmin, self.xmax, self.ymin, self.ymax, self.zmin, aabb.zmin))
        return subtracted

    def can_contain(self, aabb: "Aabb") -> bool:
        """
        Checks if the current AABB can completely contain the given AABB.

        Parameters:
            aabb (Aabb): Another AABB to check containment.

        Returns:
            bool: True if the current AABB can contain the given AABB, False otherwise.
        """
        return self.l >= aabb.l and self.w >= aabb.w and self.h >= aabb.h

    def __ge__(self, aabb: "Aabb") -> bool:
        """
        Checks if the current AABB completely contains the given AABB.

        Parameters:
            aabb (Aabb): Another AABB to compare.

        Returns:
            bool: True if the current AABB contains the given AABB, False otherwise.
        """
        return (
            self.xmin <= aabb.xmin and self.xmax >= aabb.xmax and
            self.ymin <= aabb.ymin and self.ymax >= aabb.ymax and
            self.zmin <= aabb.zmin and self.zmax >= aabb.zmax
        )

    def __str__(self) -> str:
        """
        Returns a string representation of the AABB.

        Returns:
            str: A string describing the AABB.
        """
        return (f"Aabb(xmin={self.xmin}, xmax={self.xmax}, "
                f"ymin={self.ymin}, ymax={self.ymax}, "
                f"zmin={self.zmin}, zmax={self.zmax})")



class Aabb:
    """
    Represents an Axis-Aligned Bounding Box (AABB), a cuboid with location and dimensions.

    Attributes:
        xmin, xmax (int): Minimum and maximum x-coordinates.
        ymin, ymax (int): Minimum and maximum y-coordinates.
        zmin, zmax (int): Minimum and maximum z-coordinates.
        l, w, h (int): Length, width, and height of the cuboid.
        volume (int): Volume of the cuboid, calculated as l * w * h.
    """

    def __init__(self, xmin: int, xmax: int, ymin: int, ymax: int, zmin: int, zmax: int):
        """
        Initializes an AABB with its coordinates and calculates its dimensions and volume.

        Parameters:
            xmin, xmax (int): Minimum and maximum x-coordinates.
            ymin, ymax (int): Minimum and maximum y-coordinates.
            zmin, zmax (int): Minimum and maximum z-coordinates.

        Raises:
            ValueError: If any maximum coordinate is less than or equal to its corresponding minimum.
        """
        if xmax <= xmin or ymax <= ymin or zmax <= zmin:
            raise ValueError("Maximum coordinates must be greater than minimum coordinates.")
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax
        self.zmin = zmin
        self.zmax = zmax
        self.l = xmax - xmin
        self.w = ymax - ymin
        self.h = zmax - zmin
        self.volume = self.l * self.w * self.h

    def strict_intersects(self, aabb: "Aabb") -> bool:
        """
        Checks if the given AABB strictly intersects with the current AABB.

        Parameters:
            aabb (Aabb): Another AABB to check for intersection.

        Returns:
            bool: True if the two AABBs strictly intersect, False otherwise.
        """
        return (
            self.xmin < aabb.xmax and self.xmax > aabb.xmin and
            self.ymin < aabb.ymax and self.ymax > aabb.ymin and
            self.zmin < aabb.zmax and self.zmax > aabb.zmin
        )

    def intersects(self, aabb: "Aabb") -> bool:
        """
        Checks if the given AABB intersects with or touches the current AABB.

        Parameters:
            aabb (Aabb): Another AABB to check for intersection.

        Returns:
            bool: True if the two AABBs intersect or touch, False otherwise.
        """
        return (
            self.xmin <= aabb.xmax and self.xmax >= aabb.xmin and
            self.ymin <= aabb.ymax and self.ymax >= aabb.ymin and
            self.zmin <= aabb.zmax and self.zmax >= aabb.zmin
        )

    def can_contain(self, aabb: "Aabb") -> bool:
        """
        Checks if the current AABB can completely contain the given AABB.

        Parameters:
            aabb (Aabb): Another AABB to check containment.

        Returns:
            bool: True if the current AABB can contain the given AABB, False otherwise.
        """
        return self.l >= aabb.l and self.w >= aabb.w and self.h >= aabb.h

    def __ge__(self, aabb: "Aabb") -> bool:
        """
        Checks if the current AABB completely contains the given AABB.

        Parameters:
            aabb (Aabb): Another AABB to compare.

        Returns:
            bool: True if the current AABB contains the given AABB, False otherwise.
        """
        return (
            self.xmin <= aabb.xmin and self.xmax >= aabb.xmax and
            self.ymin <= aabb.ymin and self.ymax >= aabb.ymax and
            self.zmin <= aabb.zmin and self.zmax >= aabb.zmax
        )

    def __str__(self) -> str:
        """
        Returns a string representation of the AABB.

        Returns:
            str: A string describing the AABB.
        """
        return (f"Aabb(xmin={self.xmin}, xmax={self.xmax}, "
                f"ymin={self.ymin}, ymax={self.ymax}, "
                f"zmin={self.zmin}, zmax={self.zmax})")



class Space(Aabb):
    """
    Represents a space (free cuboid) within a container, with additional properties such as 
    Manhattan distance to the closest corner and vertical stability.

    Attributes:
        manhattan (int): The Manhattan distance to the closest corner of the space to a block's corner.
        corner_point (list[int]): The coordinates of the closest corner of the space.
        filling (str): Static variable defining the filling method ("origin", "bottom-up", "free").
        vertical_stability (bool): Static variable indicating if vertical stability is enforced.
    """
    filling: str = "origin"
    vertical_stability: bool = True

    def __init__(
        self,
        xmin: int,
        xmax: int,
        ymin: int,
        ymax: int,
        zmin: int,
        zmax: int,
        block: Aabb,
    ):
        """
        Initializes a Space object.

        Parameters:
            xmin, xmax, ymin, ymax, zmin, zmax (int): Coordinates defining the space.
            block (Aabb): The block representing the container or related bounding box.

        Raises:
            ValueError: If the coordinates are invalid (e.g., xmax <= xmin).
        """
        super().__init__(xmin, xmax, ymin, ymax, zmin, zmax)
        self.container_block = block
        self.corner_point = [xmin, ymin, zmin]

        # Compute Manhattan distance and closest corner based on filling strategy.
        xdist, ydist, zdist = xmin, ymin, zmin
        if Space.filling == "bottom-up":
            zdist = 1000 * zmin  # Increase priority for bottom-up filling.

        if block.l - xmax < xmin and Space.filling != "origin":
            xdist = block.l - xmax
            self.corner_point[0] = xmax

        if block.w - ymax < ymin and Space.filling != "origin":
            ydist = block.w - ymax
            self.corner_point[1] = ymax

        if block.h - zmax < zmin and Space.filling == "free":
            zdist = block.h - zmax
            self.corner_point[2] = zmax

        self.manhattan = xdist + ydist + zdist

    def subtract(self, aabb: Aabb, container_block: Aabb) -> list["Space"]:
        """
        Subtracts a given AABB from the current space and returns the resulting subspaces.

        Parameters:
            aabb (Aabb): The AABB to subtract.
            container_block (Aabb): The container block defining boundaries.

        Returns:
            list[Space]: A list of resulting Space objects.
        """
        subspaces = []

        if aabb.xmax < self.xmax:
            subspaces.append(Space(aabb.xmax, self.xmax, self.ymin, self.ymax, self.zmin, self.zmax, container_block))

        if aabb.ymax < self.ymax:
            subspaces.append(Space(self.xmin, self.xmax, aabb.ymax, self.ymax, self.zmin, self.zmax, container_block))

        if aabb.zmax < self.zmax:
            if not Space.vertical_stability:
                subspaces.append(Space(self.xmin, self.xmax, self.ymin, self.ymax, aabb.zmax, self.zmax, container_block))
            else:
                subspaces.append(Space(aabb.xmin, aabb.xmax, aabb.ymin, aabb.ymax, aabb.zmax, self.zmax, container_block))

        if aabb.xmin > self.xmin:
            subspaces.append(Space(self.xmin, aabb.xmin, self.ymin, self.ymax, self.zmin, self.zmax, container_block))

        if aabb.ymin > self.ymin:
            subspaces.append(Space(self.xmin, self.xmax, self.ymin, aabb.ymin, self.zmin, self.zmax, container_block))

        if aabb.zmin > self.zmin:
            subspaces.append(Space(self.xmin, self.xmax, self.ymin, self.ymax, self.zmin, aabb.zmin, container_block))

        return subspaces


    
class FreeSpace:
    """
    Represents the free spaces inside a block, consisting of a list of AABBs (spaces).
    
    Attributes:
        spaces (list[Space]): A list of free space cuboids (AABB objects).
    """
    spaces: list

    def __init__(self, aabb: Space = None):
        """
        Initializes the FreeSpace object.
        
        Parameters:
            aabb (Space, optional): An initial AABB to add to the free space list.
        """
        self.spaces = []
        if aabb is not None:
            self.spaces.append(aabb)

    def remove_nonmaximal_spaces(self, aabbs: list[Space]):
        """
        Removes spaces that are completely contained within other spaces.

        Parameters:
            aabbs (list[Space]): A list of spaces to process.
        """
        # Sort spaces by volume in descending order
        aabbs.sort(key=lambda aabb: aabb.volume, reverse=True)
        to_remove = set()

        for i in range(len(aabbs)):
            for j in range(i + 1, len(aabbs)):
                if j in to_remove:
                    continue
                if aabbs[i] >= aabbs[j]:
                    to_remove.add(j)

        # Remove non-maximal spaces
        aabbs[:] = [aabbs[i] for i in range(len(aabbs)) if i not in to_remove]

    def crop(self, aabb: Space, container_block: Space):
        """
        Subtracts a given AABB from all spaces and updates the free space list.

        Parameters:
            aabb (Space): The AABB to subtract.
            container_block (Space): The container block defining boundaries.
        """
        new_spaces = []
        to_remove = []

        for space in self.spaces:
            if space.intersects(aabb):
                if space.strict_intersects(aabb):
                    new_spaces.extend(space.subtract(aabb, container_block))
                else:
                    new_spaces.append(space)

                to_remove.append(space)

        for space in to_remove:
            self.spaces.remove(space)

        self.remove_nonmaximal_spaces(new_spaces)
        self.spaces.extend(new_spaces)

    def closest_space(self) -> Space | None:
        """
        Finds the free space closest to the origin based on Manhattan distance.

        Returns:
            Space or None: The closest free space, or None if no spaces are available.
        """
        return min(self.spaces, key=lambda space: space.manhattan, default=None)

    def filter(self, items: dict) -> None:
        """
        Removes all spaces that cannot fit any of the provided item types.

        Parameters:
            items (dict[Boxtype, int]): A dictionary mapping item types to their quantities.
        """
        to_remove = []
        for space in self.spaces:
            if not any(
                items[item] > 0 and space.l >= item.l and space.w >= item.w and space.h >= item.h
                for item in items
            ):
                to_remove.append(space)

        for space in to_remove:
            self.spaces.remove(space)

    def __str__(self) -> str:
        """
        Converts the free space list to a string representation.

        Returns:
            str: A string describing all free spaces.
        """
        return "\n".join(str(space) for space in self.spaces)


from copy import copy
from types import NoneType


class Block:
    """
    Represents a block composed of items (boxtype and quantity) with defined dimensions and properties.
    
    Attributes:
        l (int): Length of the block.
        w (int): Width of the block.
        h (int): Height of the block.
        occupied_volume (int): Total volume occupied by items in the block.
        weight (int): Total weight of the block.
        volume (int): Total volume of the block.
        items (Itemdict): Dictionary of items (Boxtype: int).
        free_space (FreeSpace): List of free spaces in the block.
        aabbs (list): List of placed blocks as AABB objects.
        tokens (list): Additional metadata for the block.
    """
    l: int
    w: int
    h: int
    occupied_volume: int
    weight: int
    volume: int
    items: Itemdict
    free_space: FreeSpace
    aabbs: list
    tokens: list

    def __init__(self, boxtype=None, rot=True, l=0, w=0, h=0, copy_block=None, items=None):
        """
        Initializes a Block object with various configurations.
        
        Parameters:
            boxtype (Boxtype, optional): A single item to initialize the block.
            rot (bool, optional): Whether to allow rotations of the item. Default is True.
            l, w, h (int, optional): Dimensions of the block for custom initialization.
            copy_block (Block, optional): A block to copy.
            items (dict, optional): Dictionary of items to initialize the block.
        """
        if items is not None:
            # Block composed of items
            self.l, self.w, self.h = l, w, h
            self.volume = l * w * h
            self.weight = 0
            self.occupied_volume = 0
            self.items = Itemdict()
            for item, quantity in items.items():
                self.occupied_volume += item.volume * quantity
                self.weight += item.weight * quantity
                self.items[item] = quantity

        elif copy_block is not None:
            # Copy an existing block
            self.l = copy_block.l
            self.w = copy_block.w
            self.h = copy_block.h
            self.weight = copy_block.weight
            self.occupied_volume = copy_block.occupied_volume
            self.volume = copy_block.volume
            self.items = Itemdict(copy_block.items)
            self.tokens = list(copy_block.tokens)
            # TODO: Handle copying free_space and aabbs if needed

        elif boxtype is not None:
            # Block initialized from a single boxtype
            self._initialize_from_boxtype(boxtype, rot)
            self.free_space = FreeSpace()
            self.tokens = []

        else:
            # Custom dimensions
            self.l, self.w, self.h = l, w, h
            self.volume = l * w * h
            self.occupied_volume = 0
            self.weight = 0
            self.items = Itemdict()
            self.aabbs = []
            self.free_space = FreeSpace(Space(0, l, 0, w, 0, h, self))

    def _initialize_from_boxtype(self, boxtype, rot):
        """Helper function to initialize block dimensions from a boxtype."""
        self.l = self.w = self.h = 0
        if rot[0] == 'w': self.l = boxtype.w
        if rot[1] == 'w': self.w = boxtype.w
        if rot[2] == 'w': self.h = boxtype.w

        if rot[0] == 'l': self.l = boxtype.l
        if rot[1] == 'l': self.w = boxtype.l
        if rot[2] == 'l': self.h = boxtype.l

        if rot[0] == 'h': self.l = boxtype.h
        if rot[1] == 'h': self.w = boxtype.h
        if rot[2] == 'h': self.h = boxtype.h

        self.weight = boxtype.weight
        self.occupied_volume = boxtype.volume
        self.volume = boxtype.volume
        self.items = Itemdict({boxtype: 1})

    def add_block(self, block, x, y, z):
        """
        Adds a block to a specified position if there is enough free space.
        
        Parameters:
            block (Block): The block to add.
            x, y, z (int): The position to place the block.
        """
        aabb = Aabb(x, x + block.l, y, y + block.w, z, z + block.h)
        self.aabbs.append(aabb)
        self.occupied_volume += block.occupied_volume
        self.weight += block.weight
        self.items += block.items
        self.free_space.crop(aabb, block)

    def join(self, block, dim, min_fr=0.98) -> bool:
        """
        Attempts to join this block with another along a specified dimension.
        
        Parameters:
            block (Block): The block to join.
            dim (str): Dimension ('x', 'y', or 'z') to join along.
            min_fr (float): Minimum fill ratio to allow joining. Default is 0.98.
        
        Returns:
            bool: True if the blocks were successfully joined, False otherwise.
        """
        if dim == 'x':
            l = self.l + block.l
            w = max(self.w, block.w)
            h = max(self.h, block.h)
        elif dim == 'y':
            l = max(self.l, block.l)
            w = self.w + block.w
            h = max(self.h, block.h)
        elif dim == 'z':
            l = max(self.l, block.l)
            w = max(self.w, block.w)
            h = self.h + block.h
        else:
            return False

        new_volume = l * w * h
        if (self.occupied_volume + block.occupied_volume) / new_volume < min_fr:
            return False

        self.l, self.w, self.h = l, w, h
        self.volume = new_volume
        self.weight += block.weight
        self.occupied_volume += block.occupied_volume
        self.items += block.items
        return True
    
    def is_constructible(self, items):
        for item in self.items:
            if items[item] < self.items[item]:
                return False
        return True

    def __str__(self):
        return (f"Block: l={self.l}, w={self.w}, h={self.h}, weight={self.weight}, "
                f"volume={self.volume}, occupied_volume={self.occupied_volume}, "
                f"items={self.items}, ratio={self.occupied_volume_ratio()}")



class BlockList(list):
    """
    Represents a list of blocks, with functionality to generate simple and general blocks 
    and filter or evaluate them based on constraints.

    Attributes:
        items (dict): Dictionary of items (boxtype -> quantity).
        type (str): Type of block generation ("simple_blocks" or "general_blocks").
        cont (Block, optional): Container block to constrain block generation.
        min_fr (float): Minimum fill ratio for generated blocks. Default is 0.98.
        max_bl (int): Maximum number of blocks to generate. Default is 10,000.
    """

    def __init__(self, items, type: str, cont=None, min_fr=0.98, max_bl=10000, *args):
        super().__init__(*args)
        if type == "simple_blocks":
            self.generate_simple_blocks(items)
        elif type == "general_blocks":
            self.generate_general_blocks(items, cont, min_fr, max_bl)

    def generate_simple_blocks(self, items: dict):
        """
        Generates simple blocks from the provided items.
        
        Parameters:
            items (dict): Dictionary of boxtype -> quantity.
        """
        for item in items:
            self.append(Block(item, "lwh"))
            if item.rot_l:
                self.append(Block(item, "whl"))
                self.append(Block(item, "hwl"))
            if item.rot_w:
                self.append(Block(item, "lhw"))
                self.append(Block(item, "hlw"))
            if item.rot_h:
                self.append(Block(item, "wlh"))

    def generate_general_blocks(self, items: dict, cont, min_fr=0.98, max_bl=10000):
        """
        Generates general blocks by combining existing blocks and filtering based on constraints.

        Parameters:
            items (dict): Dictionary of boxtype -> quantity.
            cont (Block): Container block to constrain block generation.
            min_fr (float): Minimum fill ratio for generated blocks. Default is 0.98.
            max_bl (int): Maximum number of blocks to generate. Default is 10,000.
        """
        self.generate_simple_blocks(items)
        B = self
        P = B.copy()

        while len(B) < max_bl:
            N = []
            for b1 in P:
                for b2 in B:
                    for new_block in Block.generate_blocks(b1, b2, min_fr):
                        if new_block.is_constructible(items) and new_block <= cont:
                            N.append(new_block)
                            if len(B) + len(N) >= max_bl:
                                break
                    if len(B) + len(N) >= max_bl:
                        break
                if len(B) + len(N) >= max_bl:
                    break

            if not N:
                break
            B.extend(N)
            P = N

    @staticmethod
    def best(blocks, space, cont, eval_function, ctr_functions):
        """
        Selects the best block based on evaluation and constraints.

        Parameters:
            blocks (list): List of blocks to evaluate.
            space (FreeSpace): Current free space in the container.
            cont (Block): Container block.
            eval_function (callable): Function to evaluate blocks.
            ctr_functions (list): List of constraint functions.

        Returns:
            Block: The best block satisfying constraints and having the highest evaluation.
        """
        best_block = None
        best_eval = float("-inf")
        for block in blocks:
            if all(ctr(block, space, cont) for ctr in ctr_functions):
                ev = eval_function(block, space, cont)
                if ev > best_eval:
                    best_block = block
                    best_eval = ev
        return best_block

    @staticmethod
    def remove_unconstructable(blocks: list, items: dict):
        """
        Removes blocks that cannot be constructed with the given items.

        Parameters:
            blocks (list): List of blocks to filter.
            items (dict): Dictionary of items (boxtype -> quantity).
        """
        to_remove = [block for block in blocks if not block.is_constructible(items)]
        for block in to_remove:
            blocks.remove(block)

    def __str__(self):
        """
        Returns a string representation of the BlockList.
        """
        return "\n".join(str(block) for block in self)
