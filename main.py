import tdl
from game_objects import * 
from map import *
from random import randint
import textwrap

class Context:
    """
    
    Класс для хранения основных констант и переменных в игре.
    Передается во все основные объекты в игре.
    
    Основные константы
    
    SCREEN_WIDTH, SCREEN_HEIGHT - ширина и высота экрана
    BAR_WIDTH, MSG_X, MSG_WIDTH, MSG_HEIGHT, PANEL_Y, PANEL_HEIGHT - параметры необходимые для рисования нижней панели
    
    INVENTORY_WIDTH - ширина инвентаря
    
    """
    SCREEN_WIDTH = 80
    SCREEN_HEIGHT = 50
    BAR_WIDTH = 20
    PANEL_HEIGHT = 7
    PANEL_Y = SCREEN_HEIGHT - PANEL_HEIGHT
    MSG_X = BAR_WIDTH + 2
    MSG_WIDTH = SCREEN_WIDTH - BAR_WIDTH - 2
    MSG_HEIGHT = PANEL_HEIGHT - 1
    LIMIT_FPS = 20
    INVENTORY_WIDTH = 50 
    
    def __init__(self):
        """
        
        Основные параметры
        
        root - основная консоль
        con - вспомогательная консоль, используется как буфер
        panel - нижняя панель на консоли
        game_msgs - все сообщения в игре
        
        """
        tdl.set_font('arial10x10.png', greyscale=True, altLayout=True)
        self.con = tdl.init(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, title="Roguelike", fullscreen=False)
        tdl.setFPS(self.LIMIT_FPS)
        self.root = tdl.init(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, title="Roguelike", fullscreen=False)
        self.game_msgs = []
        self.panel = tdl.Console(self.SCREEN_WIDTH, self.PANEL_HEIGHT)
    
    
    def blit(self):
        """Сливает вспомогательную консоль con и panel с основной консолью root"""
        self.root.blit(self.con, 0, 0, self.SCREEN_WIDTH, self.SCREEN_HEIGHT, 0, 0)
        self.root.blit(self.panel, 0, self.PANEL_Y, self.SCREEN_WIDTH, self.PANEL_HEIGHT, 0, 0)
        
    def message(self, new_msg, color = (255,255,255)):
        """Записывает сообщение в лог"""
        new_msg_lines = textwrap.wrap(new_msg, self.MSG_WIDTH)

        for line in new_msg_lines:
            if len(self.game_msgs) == self.MSG_HEIGHT:
                del self.game_msgs[0]
            self.game_msgs.append((line, color))
   
class Game:
    """Класс - Игра. В нем происходит координация действий игрока и окружающего мира"""
    REALTIME = False 
    
    def __init__(self):
        """
        
        Основные парметры
        
        context - объект, в котором хранится основные константы и переменные игры
        my_map - карты игры
        player - игрок
        game_state - игра продолжается, пока данная переменная имеет значение 'playing'
        player_action - текущее действие игрока, при инициализации имеет значение None
        
        """
        self.context = Context()
        self.my_map = Map(self.context)
        start, end = self.my_map.start_room.center()
        self.player = Player(start, end, self.context)
        self.game_state = 'playing'
        self.player_action = None
    
    
    def start(self):
        """
        
        Метод запускающий игру и обрабатывающий действия игрока.
        
        Останавливается после нажатия клавиши 'ESCAPE'
        
        """
        while not tdl.event.is_window_closed():

            self.my_map.draw(self.player)
            self.draw_panel()
            tdl.flush()
            
            self.player.clear()
            self.my_map.clear()

            player_action = self.handle_keys()
            if player_action == 'exit':
                break

            if self.game_state == 'playing' and player_action != 'didnt-take-turn':
                self.monsters_move()
     
    
    def monsters_move(self):
        """После движения игрока, монстры в видимой части карты начинают двигаться к игроку и атаковать его"""
        visible_tiles = self.context.visible_tiles
        for x, y in visible_tiles:
            if self.my_map.is_monster(x, y):
                monster = self.my_map.get_monster(x, y)
                if monster.distance_to(self.player) >= 2:
                    dx, dy = monster.step(self.player.x, self.player.y)
                    if not self.my_map.is_block(monster.x + dx, monster.y + dy):
                        monster.move(dx, dy)
                        self.my_map.push_monster(x + dx, y + dy, monster)
                        self.my_map.remove_monster(x, y)
                        
                elif not self.player.is_dead():
                    monster.attack(self.player)
                elif self.player.is_dead():
                    self.game_state = "dead"
            
    
    def handle_keys(self):
        """
        
        Метод, который обрабатывает все нажатия клавиш в игре
        
        Помимо стрелок возможно нажатие:
        
        Alt+Enter - для полного расширения экоана
        Ecs - для выхода из игры
        g - поднять предмет, в клетке, в которой стоит игрок
        i - открыть инвентарь, чтобы закрыть нужно нажать Esc
        
        После каждого хода карта обновляется
        
        Внутри Инвентаря:
        
        Если он не пустой, то рядом с предметом, стоит буква, при нажатии на которую предмет
        - одеватся, если не был использован
        - снимается, если был использован
        - зелье выпивается.
        
        """
        if self.REALTIME:
            keypress = False
            for event in tdl.event.get():
                if event.type == 'KEYDOWN':
                   user_input = event
                   keypress = True
            if not keypress:
                return
     
        else: 
            user_input = tdl.event.key_wait()
     
        if user_input.key == 'ENTER' and user_input.alt:
            tdl.set_fullscreen(True)
     
        elif user_input.key == 'ESCAPE':
            return 'exit'  #exit game
     
        if self.game_state == 'playing':
            #movement keys
            step = (0, 0) 
            if user_input.key == 'UP':
                step = (0, -1)
        
            elif user_input.key == 'DOWN':
                step = (0, 1)
        
            elif user_input.key == 'LEFT':
                step = (-1, 0)
        
            elif user_input.key == 'RIGHT':
                step = (1, 0)
            
            
            if not step == (0, 0):
                self.my_map.recompute()
                x = self.player.x + step[0]
                y = self.player.y + step[1]
                if self.my_map.is_monster(x, y):
                    monster = self.my_map.get_monster(x, y)
                    self.player.attack(monster)
                    if monster.is_dead():
                        self.my_map.remove_monster(x, y)
                elif not self.my_map.is_block(x, y):
                    self.player.move(step[0], step[1])
            else:
                
                 
                if user_input.text == 'g':
                    self.my_map.recompute()
                    x = self.player.x
                    y = self.player.y
                    if self.my_map.is_item(x, y):
                        if not self.player.is_full():
                            item = self. my_map.get_item(x, y)
                            self.player.pick_up(item)
                        else:
                            self.context.message('Your backpack full', (255, 0, 0))
                          

                if user_input.text == 'i':
                    self.my_map.recompute()
                    items = self.player.get_items()
                    while True:
                        index_item = self.menu('Press the key next to an item to use it, or escape to cancel.\n',items,  self.context.INVENTORY_WIDTH)
                        if index_item is None:
                            break
                        if index_item >= 0 and index_item < len(items):
                            self.player.use(index_item)
                        self.draw_panel()

                return 'didnt-take-turn'
                
            
    def menu(self, header, options, width):
        """
        
        Метод, который рисует инвентарь. Выбрасывает исключение типа ValueError, если
        количество объектов в инвентаре превышает 26.
        
        Рядом с каждым объектом указаны его характеристики и метка 'in use', если объект надет на игроке
    
        """
        
        if len(options) > 26:
            raise ValueError ('Cannot have a menu with more than 26 options.')
        
        header_wrapped = []
        for header_line in header.splitlines():
            header_wrapped.extend(textwrap.wrap(header_line, width))
        header_height = len(header_wrapped)
        height = len(options) + header_height + 1


        window = tdl.Console(width, height)
        window.draw_rect(0, 0, width, height, None, fg=(255, 255, 255), bg=None)
        for i, line in enumerate(header_wrapped):
            window.draw_str(0, 0 + i, header_wrapped[i])

        
        y = header_height
        letter_index = ord('a')
        if len(options) == 0:
            text = 'Inventory is empty'
            window.draw_str(0, y, text, bg=None) 
        
        else:
            for item in options:
                if item.name != 'potion' and item.use:
                    text = '({}) {} hp+ {} damage+ {} defense+ {} in use'.format(chr(letter_index), item.name, item.hp, item.power, item.defense)
                    window.draw_str(0, y, text, fg=(127,20,63), bg=None)
                elif item.name != 'potion':
                    text = '({}) {} hp+ {} damage+ {} defense+ {}'.format(chr(letter_index), item.name, item.hp, item.power, item.defense)
                    window.draw_str(0, y, text, bg=None)
                else:
                    text = '({}) {} hp+ {}'.format(chr(letter_index), item.name, item.hp)
                    window.draw_str(0, y, text, bg=None)
                y += 1
                letter_index += 1

        x = self.context.SCREEN_WIDTH//2 - width//2
        y = self.context.SCREEN_HEIGHT//2 - height//2
        self.context.root.blit(window, x, y, width, height, 0, 0)
        tdl.flush()
        
        key = tdl.event.key_wait()
        
        key_char = key.char
        if key_char == '':
            key_char = ' ' 
            
        if key.key == "ESCAPE":
            return None
        
        index = ord(key_char) - ord('a')
        return index 
        
    def draw_panel(self):
        """Рисует внизу консоли панель с текущими характеристиками игрока и сообщениями об основных собитиях в игре"""
        panel = self.context.panel
        self.write_msg()
        light_red = (255,114,114)
        darker_red = (127,0,0)
        self.render_bar(1, 1, self.context.BAR_WIDTH, 'HP', self.player.hp, self.player.max_hp,
            light_red, darker_red)
        panel.draw_str(1, 3, 'POWER: {:<5}'.format(self.player.power))
        panel.draw_str(1, 5, 'DEFENSE: {:<5}'.format(self.player.defense))
        self.player.draw()
        self.context.blit()
        tdl.flush()
        
        
    def write_msg(self):
        """Выводит сообщения на нижней панели"""
        panel = self.context.panel
        game_msgs = self.context.game_msgs
        panel.clear(fg=(255, 255, 255), bg=(0, 0, 0))
        y = 1
        for (line, color) in game_msgs:
            panel.draw_str(self.context.MSG_X, y, line, bg=None, fg=color)
            y += 1

        
    def render_bar(self, x, y, total_width, name, value, maximum, bar_color, back_color):
        """Рисует полоску здоровья"""
        panel = self.context.panel
        bar_width = int(float(value) / maximum * total_width)
        panel.draw_rect(x, y, total_width, 1, None, bg=back_color)
        if bar_width > 0:
            panel.draw_rect(x, y, bar_width, 1, None, bg=bar_color)
        text = name + ': ' + str(value) + '/' + str(maximum)
        x_centered = x + (total_width-len(text))//2
        panel.draw_str(x_centered, y, text, fg=(255, 255, 255), bg=None)
             

if __name__ == '__main__':
    game = Game()
    game.start()      

 
    
    
    
 



            

