from core.config import *

class Collision():
    def __init__(self):
        pass

    def check_x(self, player, enemies, map, lines, gimmicks, goal):
        self.player_map_x(player, map)
        self.player_lines_x(player, lines)
        self.enemies_map_x(enemies, map)
    
    def check_y(self, player, enemies, map, lines, gimmicks, goal):
        self.player_map_y(player, map)
        self.player_lines_y(player, lines)
        self.enemies_map_y(enemies, map)

    def check(self, player, enemies, map, lines, gimmicks, goal):
        self.player_enemies(player, enemies)
        self.player_gimmicks(player, gimmicks)
        self.player_goal(player, goal)
        self.player_window(player)
        self.enemies_bullets_map(enemies, map)
        self.map_lines(map, lines)
        self.lines_gimmicks(lines, gimmicks)

    def player_map_x(self, player, map):
        for i in map.rect:
            if player.rect.colliderect(i):
                player.collide_map_x(i)

    def player_lines_x(self, player, lines):
        if lines.mask == None:
            return
        overlap_mask = player.mask.overlap_mask(lines.mask, (-player.rect.x, -player.rect.y))
        if overlap_mask.count() == 0:
            return
        player.collide_lines_x(overlap_mask, lines.mask)

    def enemies_map_x(self, enemies, map):
        for enemy in enemies.enemies:
            for i in map.rect:
                if enemy.rect.colliderect(i):
                    enemy.collide_map_x(i)

    def player_map_y(self, player, map):
        for i in map.rect:
            if player.rect.colliderect(i):
                player.collide_map_y(i)
    
    def player_lines_y(self, player, lines):
        if lines.mask == None:
            return
        overlap_mask = player.mask.overlap_mask(lines.mask, (-player.rect.x, -player.rect.y))
        if overlap_mask.count() == 0:
            return
        player.collide_lines_y(overlap_mask, lines.mask)

    
    def enemies_map_y(self, enemies, map):
        for enemy in enemies.enemies:
            for i in map.rect:
                if enemy.rect.colliderect(i):
                    enemy.collide_map_y(i)

    def player_enemies(self, player, enemies):
        for enemy in enemies.enemies:
            for bullet in enemy.bullets:
                if player.rect.colliderect(bullet.rect):
                    bullet.collide_player(player)
            if player.rect.colliderect(enemy.rect):
                print("collide")
                enemy.collide_player(player)
    
    def player_gimmicks(self, player, gimmicks):
        for gimmick in gimmicks.gimmicks:
            if player.rect.colliderect(gimmick.rect):
                gimmick.collide_player(player)
    
    def player_goal(self, player, goal):
        if player.rect.colliderect(goal.rect):
            return True
        return False
    
    def player_window(self, player):
        if player.rect.left < 0:
            player.rect.left = 0
        if player.rect.right > WINDOW_SIZE[X]:
            player.rect.right = WINDOW_SIZE[X]
        if player.rect.top < 0:
            player.rect.top = 0
        if player.rect.bottom > WINDOW_SIZE[Y]:
            player.rect.bottom = WINDOW_SIZE[Y]

    def enemies_bullets_map(self, enemies, map):
        for enemy in enemies.enemies:
            for bullet in enemy.bullets:
                for i in map.rect:
                    if bullet.rect.colliderect(i):
                        bullet.collide_map()

    
    def map_lines(self, map, lines):
        for magic in lines.magics:
            for i in map.rect:
                if magic.rect.colliderect(i):
                    magic.collide_map()
    
    def lines_gimmicks(self, lines, gimmicks):
        for magic in lines.magics:
            for gimmick in gimmicks.gimmicks:
                if magic.rect.colliderect(gimmick.rect):
                    gimmick.collide_magic(magic)