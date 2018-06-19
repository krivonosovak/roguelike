from random import randint
from game_objects import GameObject, Troll, Orc, ObjectFactory
import tdl



class Tile:
    """Блоки для построения карты"""
    
    def __init__(self, blocked, block_sight=None):
        """
        
        Основные параметры:
        blocked - True, если это стена
        block_sight  True - если этот блок не видим игроку
        explored - изначально False; после того как игрок попадает в видимость игрока, становится True
        
        """
        self.blocked = blocked
        self.explored = False
        if block_sight is None: 
            block_sight = blocked
        self.block_sight = block_sight


class Rect:
    """Класс прямоугольник, используется для моделирования комнат"""
    
    def __init__(self, x, y, w, h):
        """
        Основные параметры
        
        x1, y1 - координаты левого нижнего угла
        x2 y2 - координаты правого верхнего угла
        w - ширина прямоугольника
        h - высота прямоугольника
        """
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h
 
    def center(self):
        """Возвращает точку-центр прямоугольника"""
        center_x = (self.x1 + self.x2) // 2
        center_y = (self.y1 + self.y2) // 2
        return (center_x, center_y)
 
    def intersect(self, other):
        """Провека на пересечение с прямоугольником other"""
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1) 


class MapFactory:
    """
    
    Фабрика для создания лабиринта
    
    Основные константы
    
    MAP_WIDTH - ширина карты
    MAP_HEIGHT - высота карты
    ROOM_MAX_SIZE - максимальный размер комнаты в лабиринте
    ROOM_MIN_SIZE - минимальный размер комнаты в лабиринте
    MAX_ROOMS - количество комнат в лабиринте
    """
    MAP_WIDTH = 80
    MAP_HEIGHT = 40
    ROOM_MAX_SIZE = 10
    ROOM_MIN_SIZE = 6
    MAX_ROOMS = 30
    
    
    def get_empty_map(self):
        """
        
        Метод создает пустую карту и рисует в ней лабиринт.
        
        Случайно создает комнаты как прямоугольники, случайно выбирая координаты левого нижнего угла, ширины и высоты.
        Создает MAX_ROOMS комнат в лабиринте и соединяет их путями.
        
        Возвращает Начальную комнату - start_room, список комнат - rooms и карту с лабиринтом - my_map.
        
        """
        my_map = [[{'wall' : Tile(True), 'monster' : None, 'item': None}
                    for y in range(self.MAP_HEIGHT)] for x in range(self.MAP_WIDTH)]
        rooms = []
        num_rooms = 0
    
        for r in range(self.MAX_ROOMS):
       
            w = randint(self.ROOM_MIN_SIZE, self.ROOM_MAX_SIZE)
            h = randint(self.ROOM_MIN_SIZE, self.ROOM_MAX_SIZE)
            x = randint(0, self.MAP_WIDTH-w-1)
            y = randint(0, self.MAP_HEIGHT-h-1)
    
            new_room = Rect(x, y, w, h)
    
            failed = False
            for other_room in rooms:
                if new_room.intersect(other_room):
                    failed = True
                    break
    
            if not failed:
                self.create_room(new_room, my_map)
                (new_x, new_y) = new_room.center()
    
                if num_rooms == 0:
                    start_room = new_room
                else:
                    (prev_x, prev_y) = rooms[num_rooms-1].center()
    
                    if randint(0, 1):
                        self.create_h_tunnel(prev_x, new_x, prev_y, my_map)
                        self.create_v_tunnel(prev_y, new_y, new_x, my_map)
                    else:
                        self.create_v_tunnel(prev_y, new_y, prev_x, my_map)
                        self.create_h_tunnel(prev_x, new_x, new_y, my_map)
                rooms.append(new_room)
                num_rooms += 1
        return start_room, rooms, my_map
    
    def create_room(self, room, my_map):
        """
        
        Все координаты внутри прямоугольника room становятся
        разблокированными и видимыми
        
        """
        for x in range(room.x1 + 1, room.x2):
            for y in range(room.y1 + 1, room.y2):
                my_map[x][y]["wall"].blocked = False
                my_map[x][y]["wall"].block_sight = False
     
    def create_h_tunnel(self, x1, x2, y, my_map):
        """Создает горизонтальный тунель между координатами (x1, y) и (x2, y)"""
        for x in range(min(x1, x2), max(x1, x2) + 1):
            my_map[x][y]["wall"].blocked = False
            my_map[x][y]["wall"].block_sight = False
            
    def create_v_tunnel(self, y1, y2, x, my_map):
        """Создает горизонтальный тунель между координатами (x, y1) и (x, y2)"""
        for y in range(min(y1, y2), max(y1, y2) + 1):
            my_map[x][y]["wall"].blocked = False
            my_map[x][y]["wall"].block_sight = False
            
class Map:
    """
    
    Класс для управления картой игры.
    
    Основные константы:
    
    MAP_WIDTH и MAP_HEIGHT - ширина и высоты карты
    COLOR_WALL - цвет стен в комнате
    COLOR_GROUND - цвет пола
    MAX_ROOM_MONSTERS - максимальное количество монстров на карте
    
    """
    MAP_WIDTH = 80
    MAP_HEIGHT = 40
    COLOR_WALL = (0, 0, 100)
    COLOR_GROUND = (50, 50, 150)
    MAX_ROOM_MONSTERS = 3
    
    def __init__(self, context):
        """
        
        Основные параметры:
        
        context - объект с константами и переменными в игре
        fov_compute - флаг для перерисовки карты. Если значение True, то карта будет перерисована
        object_factory - фабрика для создания монстров и предметов
        map_factory - фабрика для создания пустого лабиринта
        
        """
        self.context = context
        self.fov_recompute = True
        self.object_factory = ObjectFactory(self.context)
        self.map_factory = MapFactory()
        self.make_map()
    
    def make_map(self):
        """Основной метод, в котором создается лабиринт и в него помещаются монстры и предметы"""
        self.start_room, self.rooms, self.map = self.map_factory.get_empty_map()
        for room in self.rooms:
            self.place_monster(room)
            self.place_item(room)
    


    def place_monster(self, room):
        """Метод, который помещает случайное количество монстров в комнату room"""
        num_monsters = randint(0, self.MAX_ROOM_MONSTERS)
        for i in range(num_monsters):
            x = randint(room.x1, room.x2)
            y = randint(room.y1, room.y2)
            if self.is_empty(x, y):
                monster = self.object_factory.get_monster(x, y)
                self.push_monster(x, y, monster)
    
    def place_item(self, room):
        """Случайно выбирает место в комнате room, не занятое другим объектом, и помещает туда новый объект"""
        x = randint(room.x1, room.x2)
        y = randint(room.y1, room.y2)
        if self.is_empty(x, y):
            self.map[x][y]['item'] = self.object_factory.get_item(x, y)
            
    def draw(self, player):
        """
        
        Метод, который рисует карты, при условии, что флаг fov_recompute = True.
        
        Выбирает область, на текущий момент видимую игроку, и для каждой координаты этой области рисует в ней объект.
        Также ранее невидимую область делает видимой.
        
        """
        if self.fov_recompute:
            self.fov_recompute = False
            self.context.visible_tiles = tdl.map.quickFOV(player.x, player.y,
                                                        self.is_visible_tile,
                                                        fov='BASIC',
                                                        radius=10,
                                                        lightWalls=True)
     
        
            for y in range(self.MAP_HEIGHT):
                for x in range(self.MAP_WIDTH):
                    visible = (x, y) in self.context.visible_tiles
                    wall = self.map[x][y]["wall"]
                    con = self.context.con
                    if not visible and wall.explored:
                        if wall.block_sight:
                            con.draw_char(x, y, None, fg=None, bg=self.COLOR_WALL)
                        else:
                            con.draw_char(x, y, None, fg=None, bg=self.COLOR_GROUND)
                    elif visible:
                        if wall.block_sight:
                            con.draw_char(x, y, None, fg=None, bg=self.COLOR_WALL)
                        else:
                            con.draw_char(x, y, None, fg=None, bg=self.COLOR_GROUND)
                        #since it's visible, explore it
                        self.map[x][y]["wall"].explored = True
                        
                    if self.is_item(x, y):
                        self.map[x][y]['item'].draw()
                    if self.is_monster(x, y):
                        self.map[x][y]["monster"].draw()
    
    
    def is_monster(self, x, y):
        """Метод, который проверяет, есть ли в данной ячеке (x, y) монстр на карте"""
        return self.map[x][y]["monster"] is not None
    
    def get_monster(self, x, y):
        """Метод, который возвращает монстра из данной ячеки (x, y) на карте"""
        return self.map[x][y]["monster"]
    
    def push_monster(self, x, y, monster):
        """Метод, который добавляет монстра в данную ячеку (x, y) на карте"""
        self.map[x][y]["monster"] = monster
    
    def remove_monster(self, x, y):
        """Метод, который удаляет монстра из данной ячеки (x, y) на карте"""
        self.map[x][y]["monster"] = None
        
    def recompute(self):
        """Метод, который выставляет значение fov_recompute карты в True"""
        self.fov_recompute = True
    
    def is_block(self, x, y):
        """

        Проверка, является ли данная ячейка (x, y) на карте заблокированной.
        
        Ячейка заблокированна, если на ней стоит монстр или это стена комнаты.

        """
        return self.map[x][y]["wall"].blocked or self.is_monster(x, y)
        
    def is_visible_tile(self, x, y):
        """Возвращает True, если область доступна для передвижения"""
        if x >= self.MAP_WIDTH or x < 0:
            return False
        elif y >= self.MAP_HEIGHT or y < 0:
            return False
        elif self.map[x][y]["wall"].blocked:
            return False
        elif self.map[x][y]["wall"].block_sight:
            return False
        else:
            return True
            
    def is_item(self, x, y):
        """Проверяет есть ли в ячейке (x, y) на карте какой-либо предмет"""
        return self.map[x][y]['item'] is not None
        
    def is_empty(self, x, y):
        """
        
        Проверяет пустая ли (x, y) ячейка.
        
        Ячейка пустая, если она доступна и в ней нет предмета или монстра.

        """
        return self.is_visible_tile(x, y) and not self.is_monster(x, y) and not self.is_item(x, y)
    
    def get_item(self, x, y):
        """Возвращает предмет, который лежит в ячейке (x, y)"""
        item = self.map[x][y]['item']
        self.map[x][y]['item'] = None
        return  item
        
    def clear(self):
        """Очищает всю карту"""
        for y in range(self.MAP_HEIGHT):
            for x in range(self.MAP_WIDTH):
                if self.is_monster(x, y):
                    self.map[x][y]["monster"].clear()
      