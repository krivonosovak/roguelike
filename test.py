import unittest
from main import Context
from game_objects import *
from map import *

class TestFighter(unittest.TestCase):
    def setUp(self):
        self.context = Context()
        self.white = (255, 255, 255)
        
    def tearDown(self):
        self.context = None

    def test_death(self):
        # given
        health = 10
        fighter = Fighter(0, 0, '', self.white, self.context, health, 0, 0)
        # when
        fighter.take_damage(health)
        # then
        self.assertTrue(fighter.is_dead())
        
    def test_move(self):
        # given
        x0 = 0
        y0 = 0
        fighter = Fighter(x0, y0, '', self.white, self.context, 10, 0, 0)
        dx = -5
        dy = 19
        # when
        fighter.move(dx, dy)
        # then
        self.assertEqual(fighter.x, x0+dx)
        self.assertEqual(fighter.y, y0+dy)
        
class TestInventoryAndItems(unittest.TestCase):
    def setUp(self):
        self.context = Context()
        self.player = Player(0, 0, self.context)
        
    def tearDown(self):
        self.player = None
        self.context = None
        
    def test_pickUp(self):
        # given
        potion = Potion(0, 0, self.context, 100)
        armor = Armor(0, 0, self.context, 'armor', 10, 10, 10)
        inventory = Inventory(self.player)
        # when
        inventory.pick_up(potion)
        inventory.pick_up(armor)
        inventory.use(1)
        # then
        self.assertEqual(len(inventory.backpack), 2)        
        
    def test_wearArmor(self):
        # given
        potion = Potion(0, 0, self.context, 100)
        armor = Armor(0, 0, self.context, 'armor', 10, 10, 10)
        inventory = Inventory(self.player)
        # when
        inventory.pick_up(potion)
        inventory.pick_up(armor)
        inventory.use(1)
        # then
        self.assertEqual(self.player.max_hp, 30)
        
    def test_takeOffArmor(self):
        # given
        potion = Potion(0, 0, self.context, 100)
        armor = Armor(0, 0, self.context, 'armor', 10, 10, 10)
        inventory = Inventory(self.player)
        # when
        inventory.pick_up(potion)
        inventory.pick_up(armor)
        inventory.use(1)
        inventory.use(1)
        # then
        self.assertEqual(self.player.max_hp, 20)
        
    def test_takePotion(self):
        # given
        potion = Potion(0, 0, self.context, 100)
        armor = Armor(0, 0, self.context, 'armor', 10, 10, 10)
        inventory = Inventory(self.player)
        # when
        inventory.pick_up(potion)
        inventory.pick_up(armor)
        inventory.use(1)
        inventory.use(0)
        # then
        self.assertEqual(self.player.hp, 30)
        self.assertEqual(self.player.max_hp, 30)
        
        
class TestMonster(unittest.TestCase):
    def setUp(self):
        self.context = Context()
        
    def tearDown(self):
        self.context = None

    def test_step(self):
        # given
        x0, y0 = 0, 0
        troll = Troll(x0, y0, 10, 10, 10, self.context)
        # when
        dx, dy = troll.step(0, 2)
        # then
        self.assertEqual(dx, 0)
        self.assertEqual(dy, 1)

    def test_distance(self):
        # given
        troll = Troll(0, 0, 10, 10, 10, self.context)
        other = Troll(3, 4, 10, 10, 10, self.context)
        # when
        dd = troll.distance_to(other)
        # then
        self.assertEqual(dd, 5)
        

class TestRect(unittest.TestCase):
    
    def test_center(self):
        # given
        rect = Rect(0, 0, 4, 6)
        # when
        center = rect.center()
        # then
        self.assertEqual(center, (2, 3))
        
    def test_intersect(self):
        # given
        rect   = Rect(0, 0, 4, 6)
        other  = Rect(0, 0, 1, 1)
        other2 = Rect(5, 6, 1, 1)
        # then
        self.assertTrue(rect.intersect(other))
        self.assertFalse(rect.intersect(other2))
        
class TestMap(unittest.TestCase):
    def setUp(self):
        self.context = Context()
        self.my_map = Map(self.context)
        self.my_map.map = [[{'wall' : Tile(False), 'monster' : None, 'item': None}
                    for y in range(3)] for x in range(5)]
        
    def test_contains_monster(self):
        # given
        monster = Troll(0, 0, 10, 10, 10, self.context)
        # then
        self.my_map.push_monster(0, 0, monster)
        self.assertTrue(self.my_map.is_monster(0, 0))
        
    def test_remove_monster(self):
        # given
        monster = Troll(0, 0, 10, 10, 10, self.context)
        self.my_map.push_monster(0, 0, monster)
        self.my_map.remove_monster(0, 0)
        # then
        self.assertTrue(self.my_map.is_empty(0, 0))
        self.assertFalse(self.my_map.is_monster(0, 0))
        
    def test_get_monster(self):
        # given
        monster = Troll(0, 0, 10, 10, 10, self.context)
        self.my_map.push_monster(0, 0, monster)
        # then
        self.assertEqual(self.my_map.get_monster(0, 0).name, 'Troll')
        
    def test_get_monster(self):
        # given
        monster = Troll(0, 0, 10, 10, 10, self.context)
        self.my_map.push_monster(0, 0, monster)
        self.assertEqual(self.my_map.get_monster(0, 0).name, 'Troll')
        
    def test_get_item(self):
        # given
        item = Potion(1, 1, self.context, 0)       
        self.my_map.map[1][1]['item'] = item
        # then
        self.assertEqual(self.my_map.get_item(1,1).name, 'potion')
     
    def test_get_monster(self):
        # given
        item = Potion(1, 1, self.context, 0)       
        self.my_map.map[1][1]['item'] = item
        self.assertEqual(self.my_map.get_item(1,1).name, 'potion')
    
    def test_containes_item(self):
        # given
        item = Potion(1, 1, self.context, 0)       
        self.my_map.map[1][1]['item'] = item
        # then
        self.assertTrue(self.my_map.is_item(1, 1))
        
    def tearDown(self):
        self.context = None

if __name__ == '__main__':
        unittest.main()
