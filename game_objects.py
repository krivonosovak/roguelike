from random import randint
import math



class GameObject:
    """Базовый класс для всех объектов в игре"""
    
    def __init__(self, x, y, char, color, context):
        """ 
        
        Основные парметры:
        
        x y - координаты объекта на карте
        char - символ на карте, соответствующий данному объекту
        color - цвет символа
        context - объект, который содержит все основные переменные и константы игры
        
        """
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.context = context
    

    def draw(self):
        """Рисует объект на карте, если он находится в области видимости"""
        con = self.context.con
        visible_tiles = self.context.visible_tiles
        if (self.x, self.y) in visible_tiles:
            #draw the character that represents this object at its position
            con.draw_char(self.x, self.y, self.char, self.color, bg=None)
 
    def clear(self):
        """Стирает текущий объект с карты"""
        con = self.context.con
        con.draw_char(self.x, self.y, ' ', self.color, bg=None)
        

class Fighter(GameObject):
    """Класс, в котором реализуются основные операции для передвижения и атаки объектов"""
 
    def __init__(self, x, y, char, color, context, hp, defense, power):
        """
        
        Основные параметры:
        
        max_hp - максимальное значение жизни 
        hp - текущие состояние жизни
        power - значение которое отнимается у противника при атаке
        defense - защита, значение отнимается от урона, который наносит противник    
            
        """
        self.name = "Fighter"
        GameObject.__init__(self, x, y, char, color, context)
        self.max_hp = hp
        self.hp = hp
        self.power = power
        self.defense = defense
    
    def death(self):
        """Смерть объекта"""
        if hasattr(self, 'context'):
            self.context.message(self.name + ' is dead!', (255,191,191))
        
        
    def take_damage(self, damage):
        """Нанесение ущерба(damage) данному объекту"""
        if damage > 0:
            self.hp -= damage
            if self.hp <= 0:
                self.death()

    def attack(self, target):
        """Нанесение ущерба объекту target"""
        damage = self.power - target.defense

        if damage > 0:
            self.context.message(self.name.capitalize() + ' attacks ' + target.name + 
                    ' for ' + str(damage) + ' hit points.')
            target.take_damage(damage)
        else:
            self.context.message(self.name.capitalize() + ' attacks ' + target.name + 
                    ' but it has no effect!')

    def is_dead(self):
        """Проверка на смерть"""
        return self.hp <= 0
    
    
    def move(self, dx, dy):
        """Движение объекта следующую клтеку (x + dx, y + dy)"""
        self.x += dx
        self.y += dy


class Player(Fighter):
    
    """Класс для Игрока"""
    
    def __init__(self, x, y, context):
        
        """
        Cимволом @ - изображает иконку игрока на карте
        
        Начальные характеристики игрока:
        hp = 20
        power = 4
        defense = 0
        
        name - дополнительный параметр для логирования событий
        inventory - объект для хранения и манипуляции над предметами, которые есть у игрока
        
        """
        self.name = 'Player'
        Fighter.__init__(self,  x, y, "@", (255,255,255), context, 20, 0, 4)
        self.inventory = Inventory(self)
    
    def death(self):
        """Переопределяет метод Fighter, мертвый игрок на карте изображается символом %"""
        print('You died!')
        self.char = '%'
        self.color = (191,0,0)
    
    
    def pick_up(self, item):
        """Кладет предмет item в рюкзак игрока"""
        self.inventory.pick_up(item)
        
        
    def use(self, index):
        """см. Inventory.use()"""
        self.inventory.use(index)
        
    def get_items(self):
        """Метод возвращает все объекты из рюкзака"""
        return self.inventory.backpack
        
    def is_full(self):
        """Проверка на полноты рюкзака"""
        return self.inventory.is_full()
        

class Inventory:
    """
    
    Класс-контейнер для хранения и манипуляций над предметами, которые есть у игрока
    
    Основные константы в классе:
        
    MAXCOUNT - максимальное количество предметов, которые могут храниться в инвентаре
    
    """
    MAXCOUNT = 20
    
    def __init__(self, owner):
        """
        
        Основные параметры:
            
        active - предметы, которые в данный момент надеты на игроке или используются им
        armor, boots и sword - предметы, которые игрок может "надевать"
        backpack - массив всех пердметов
        owner - игрок
        
        """
        self.active = {'armor': None, 'sword': None, 'boots': None}
        self.backpack = []
        self.owner = owner
    

    def use(self, i):
        """
        
        Метод для управления предметами в инвентаре
        
        Если предмет potion - то просто увеличивает жизнь, если это возможно
        Для других предметов, если он уже надет, то снимает предмет; если нет, то надевает
        
        """
        
        item = self.backpack[i]
        if item.name == 'potion':
            if self.owner.hp == self.owner.max_hp:
                self.owner.context.message('You are already at full health.', (255, 0, 0))
            else:
                item.apply(self.owner)
                del self.backpack[i]
                self.owner.context.message('Your wounds start to feel better! + {}'.format(item.hp), (184,114,255) )
        elif not item.use and self.active[item.name] is None:
            self.active[item.name] = item
            item.apply(self.owner)
            self.owner.context.message('You put on new {} with additional hp: {},  power: {}, defense: {}'.
                                    format(item.name, item.hp, item.power, item.defense), (184,114,255) )
        elif not item.use and self.active[item.name] is not None:
            self.owner.context.message( "some {} alredy in use".format(item.name) , (255,0,0) )
        
        elif item.use:
            self.owner.context.message('You take of {} with additional hp: {},  power: {}, defense: {}'.
                            format(item.name, item.hp, item.power, item.defense), (184,114,255))
            self.active[item.name] = None
            item.take_of(self.owner)
    
    
    def is_full(self):
        """Возвращает True если рюкзак полон"""
        return len(self.backpack) == self.MAXCOUNT
             
    def pick_up(self, item):
        """Положить предмет item в рюкзак, если это возможно"""
        if len(self.backpack) < self.MAXCOUNT:
            self.backpack.append(item)
            self.owner.context.message('You pick up {}'.format(item.name), (255,188,165))
        else:
            self.owner.context.message("You can't pick up this {} your backpack full", (255, 0, 0))
                

class Item(GameObject):
    
    """Класс для предметов"""
    
    def __init__(self,x, y, char, color, context, name, hp, damage, defense):
        """
        
        Основные параметры
        
        name - название предмета 
        hp - на сколько он увеличивает жизнь
        power - на сколько он увеличивает урон противнику
        defense - на сколько увеличивает защиту
        
        """
        GameObject.__init__(self, x, y, char, color, context)
        self.name = name
        self.hp = hp
        self.power = damage
        self.defense = defense
        


class Potion(Item):
    """Класс-зелье"""
    
    def __init__(self, x, y, context, hp):
        """
        На карте изображается символом !
        power и defense = 0
        """
        Item.__init__(self, x, y, '!', (0, 127, 0), context, 'potion', hp, 0, 0)
 
    def apply(self, owner):
        """Использование зелья - увеличение жизни игрока (owner)"""
        owner.hp = min(self.hp + owner.hp, owner.max_hp) 


class Armor(Item):
    
    """Базовый класс для предметов, которые можно надеть"""
    

    def __init__(self, x, y, context, name, hp, damage, defense):
        """
        
        На карте изображается знаком &
        
        use - дополнительное поле. True - если предмет надет, иначе False
        
        """
        Item.__init__(self, x, y, '&', (0, 127, 0), context, name, hp, damage, defense)
        self.use = False
    
    
    def apply(self, owner):
        """
        
        Надеть предмет - увеличивает соответсвующие ненулевые характеристики
        
        hp увеличивает не жизнь, а max_hp - максимальную границу для жизни
        
        """
        owner.max_hp += self.hp
        owner.power += self.power
        owner.defense += self.defense
        self.use = True
    
    def take_of(self, owner):
        """Снять предмет - уменьшает характеристики"""
        owner.max_hp -= self.hp
        owner.power -= self.power
        owner.defense -= self.defense
        self.use = False
            

class Monster(Fighter):
    """Базовый класс монстров"""
    
    def step(self, target_x, target_y):
        """Определение направления, чтобы двигаться за целью target"""
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)
        dx = int(round(dx / distance))
        dy = int(round(dy / distance))
        return dx, dy
    
    
    def distance_to(self, other):
        """Растояние до объекта"""
        dx = other.x - self.x
        dy = other.y - self.y
        return math.sqrt(dx ** 2 + dy ** 2)
    

class Troll(Monster):
    """Наследник класса Монстров - Тролль"""
    
    def __init__(self, x, y, hp, defense, power, context):
        """На карте изображается как T"""
        Fighter.__init__(self, x, y, "T", (0, 127, 0), context, hp, defense, power)
        self.name = 'Troll'

    
class Orc(Monster):
    """Наследник класса Монстров - Орк"""
    def __init__(self, x, y, hp, defense, power, context):
        """На карте изображается как О"""
        Fighter.__init__(self, x, y, "O", (0, 0, 127), context, hp, defense, power)
        self.name = 'Orc'

        
class ObjectFactory:
    """
    
    Фабрика для создания монстров и предметов
    
    Основные константы:
        
    MAXHEAL - максимальная величина, на которую может выличить зелье
    MAXHP - максимальная величина, на сколько предмет может увеличить max_hp
    MAXDAMAGE - максимальное величина, на которую предмет может увеличить power игрока
    MAXDEFENSE  - максимальная величина, на которую предмет может увеличить defense игрока

    """
    MAXHEAL = 8
    MAXHP = 10
    MAXDAMAGE = 5
    MAXDEFENSE = 5
    
    def __init__(self, context):
        """context - объкт, который хранит в себе основные констаты и переменные для игры"""
        self.context = context
    
    def get_monster(self, x, y):
        """
        
        Создание монстра
        
        с 80% вероятностью возвращает Орка, иначе Тролля
        
        """
        monster = None
        if randint(0, 100) < 80:
            monster = Orc(x, y, 5, 0, 2, self.context)
        else:
            monster = Troll(x, y, 5, 1, 3, self.context)
        return monster
        
    def get_item(self, x, y):
        """
        
        Создание предмета.
        
        С одинаковой вероятностью создается 
        
        potion - при использовании увеличивает только hp
        armor - при использовании увеличивает только max_hp и defense
        boots - при использовании увеличивает только max_hp и defense
        sword - при использовании увеличивает только power
        
        """
        
        item = None
        type = randint(1, 4)
        hp = randint(0, self.MAXHP)
        defense = randint(0, self.MAXDEFENSE)
        if type == 1:
            hp = randint(1, self.MAXHEAL)
            item =  Potion(x, y, self.context, hp)
        elif type == 2:
            item = Armor(x, y, self.context, 'armor', hp, 0, defense)
        elif type == 3:
            item = Armor(x, y, self.context, 'boots', hp, 0, defense)
        elif type == 4:
            damage = randint(1, self.MAXDAMAGE)
            item = Armor(x, y, self.context, 'sword', 0, damage, 0)
        return item
        


    
    