from Tkinter import *
from math import cos,radians,sin,atan2,degrees,pi
from random import randint
from collections import defaultdict

class Game:
    def __init__(self):
        self.pressed = {}
        self.bullets = []
        self.enemies = []
        self._create_ui()
        self.paused = False
        self.kills = 0
        self.spawn = 1.0

    def start(self):
        self.player = Player(self.canvas,x=250,y=250)
        self._add_enemy()
        self._animation_loop()
        self.root.mainloop()

    def _create_ui(self):
        self.root = Tk()
        self.canvas = Canvas(width=500,height=500)
        self.canvas.pack()

        self._set_bindings()
    
    def _animate(self):
        dead = []
        if not self.paused:
            if not any(self.pressed[c] for c in 'wasd'):
                pass
            else:
                if self.pressed["w"]: self.player.move_up()
                if self.pressed["s"]: self.player.move_down()
                if self.pressed["a"]: self.player.move_left()
                if self.pressed["d"]: self.player.move_right()
                self.player.redraw()
            for e in self.enemies:
                if e.contains_point(self.player.x,self.player.y):
                    print "YOU LOST\nKILLS: {}".format(self.kills)
                    self._unset_bindings()
                    return False
                e.redraw()

            for b in self.bullets:            
                if ( 0 <= b.x1 <= 500 and 0 <= b.y1 <= 500):
                    for e in self.enemies:
                        if e.contains_point(b.x1,b.y1):
                            e.hurt(b.dmg)
                            if e.dead:
                                dead.append(e)
                            b.hit = True
                    if b.hit:
                        self.canvas.delete(b.img)
                        dead.append(b)
                    else:
                        b.redraw()
                else:
                    dead.append(b)

            for thing in dead:

                if isinstance(thing,Enemy):
                    self.canvas.delete(thing.img)
                    self.enemies.remove(thing)
                    self.kills += 1
                    self.spawn += 0.2
                    for _ in xrange(int(self.spawn)):
                        self._add_enemy()
                else:
                    self.bullets.remove(thing)
        return True

    def _animation_loop(self):
        if self._animate():
            self.root.after(48, self._animation_loop)

    def _change_pause(self,event):
        if event.type == '8':
            self.paused = True
        elif event.type == '7':
            self.paused = False
        elif event.type == "2":
            if self.paused == False:
                self.paused = True
            else:
                self.paused = False

    def _add_enemy(self):
        self.enemies.append(Enemy(self.canvas,randint(0,500),randint(0,500)))

    def _set_bindings(self):
        for char in "wasd":
            self.root.bind("<KeyPress-{}>".format(char),self._pressed)
            self.root.bind("<KeyRelease-{}>".format(char),self._released)
            self.pressed[char] = False
        self.root.bind("<ButtonPress-1>", self._shoot)
        self.root.bind("<Enter>", self._change_pause)
        self.root.bind("<Leave>", self._change_pause)
        self.root.bind("<space>", self._change_pause)

    def _unset_bindings(self):
        for char in "wasd":
            self.root.unbind("<KeyPress-{}>".format(char))
            self.root.unbind("<KeyRelease-{}>".format(char))
        self.root.unbind("<ButtonPress-1>")
        self.root.unbind("<Enter>")
        self.root.unbind("<Leave>")
        self.root.unbind("<space>")

    def _shoot(self,event):
        ox,oy = self.canvas.coords(self.player.img)
        ex = event.x
        ey = event.y
        self.bullets.append(Bullet(self.canvas,ox,oy,ex,ey))

    def _pressed(self,event):
        self.pressed[event.char] = True

    def _released(self,event):
        self.pressed[event.char] = False

class Bullet:
    def __init__(self,canvas,startx,starty,clickx,clicky):
        self.canvas = canvas
        self.x1 = startx
        self.y1 = starty
        self.x2 = clickx
        self.y2 = clicky
        self.degs = self.move_degrees(self.x1,self.y1,self.x2,self.y2)
        self.img = self.canvas.create_oval(self.x1,self.y1,self.x1+6,self.y1+3,fill='black')
        self.dmg =  2
        self.hit = False
        self.speed = 15

    def redraw(self):
        self.canvas.delete(self.img)
        change_x,change_y = self.xy_changes(self.degs,self.speed)
        self.x1 += change_x
        self.y1 += change_y
        self.img = self.canvas.create_oval(self.x1,self.y1,self.x1+6,self.y1+3,fill='black')

    def move_degrees(self,x1,y1,x2,y2):
        dx = x2-x1
        dy= y2-y1
        rads = atan2(dy,dx)
        rads %= 2*pi
        return degrees(rads)

    def xy_changes(self,d,m):
        return m*cos(radians(d)),m*sin(radians(d))
        
class Enemy:
    def __init__(self,canvas,x,y):
        self.x = x
        self.y = y
        self.canvas = canvas
        self.hp = 10
        self.sprites = esprites
        self.sprite_direction = "down"
        self.sprite_frame = 0
        self.img =  self.canvas.create_image(self.x,self.y,image=self.sprites[self.sprite_direction][self.sprite_frame])
        self.dead = False

    def contains_point(self,x,y):
        try:
            l,t,r,b = self.canvas.bbox(self.img)
        except TypeError:
            return False
        return l <= x <= r and t <= y <= b

    def hurt(self,dmg):
        self.hp -= dmg
        if self.hp <= 0:
            self.dead = True

    def move_degrees(self,x1,y1,x2,y2):
        dx = x2-x1
        dy= y2-y1
        rads = atan2(dy,dx)
        rads %= 2*pi
        return degrees(rads)

    def xy_changes(self,d,m):
        return m*cos(radians(d)),m*sin(radians(d))

    def redraw(self):
        self.degs = self.move_degrees(self.x,self.y,g.player.x,g.player.y)
        change_x,change_y = self.xy_changes(self.degs,3)
        if change_x > 1:
            self.sprite_direction = "right"
        elif change_x < -1:
            self.sprite_direction = "left"
        if change_y > 1:
            self.sprite_direction = "down"
        elif change_y < -1:
            self.sprite_direction = "up"
        self.canvas.delete(self.img)
        self.x += change_x
        self.y += change_y
        self.img = self.canvas.create_image(self.x,self.y,image=self.sprites[self.sprite_direction][self.sprite_frame])
        self.sprite_frame = (self.sprite_frame+1)%4


class Player:
    def __init__(self,canvas,x,y):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.sprite_direction = "down"
        self.sprite_frame = 0
        self.sprites = psprites
        self.speed = 6
        self.img = self.canvas.create_image(self.x,self.y,image=self.sprites[self.sprite_direction][self.sprite_frame])
        
        self.redraw()

    def move_up(self):
        self.sprite_direction = "up"
        self.y = max(self.y - self.speed, 0)
    def move_down(self):
        self.sprite_direction = "down"
        self.y = min(self.y + self.speed, 500)
    def move_left(self):
        self.sprite_direction = "left"
        self.x = max(self.x - self.speed, 0)
    def move_right(self):
        self.sprite_direction = "right"
        self.x = min(self.x + self.speed, 500)

    def redraw(self):
        self.canvas.delete(self.img)
        self.img = self.canvas.create_image(self.x,self.y,image=self.sprites[self.sprite_direction][self.sprite_frame])
        self.sprite_frame = (self.sprite_frame+1)%4

class LoadedSprite:
    def __init__(self,spritesheet):
        self.spritesheet = PhotoImage(file=spritesheet)
        self.sprites = defaultdict(list)
        self._sprites()

    def _subimage(self,src,l,t,r,b):
        dst = PhotoImage()
        dst.tk.call(dst,'copy', src, '-from',l,t,r,b,'-to',0,0)
        return dst

    def _sprites(self):
        for row,d in enumerate(['down','left','right','up']):
            for col in xrange(4):
                self.sprites[d].append(self._subimage(self.spritesheet,32*col,48*row,32*(col+1),48*(row+1)))
    
    def __getitem__(self,key):
        return self.sprites[key]


if __name__ == "__main__":
    g = Game()
    psprites = LoadedSprite("C:\Users\Seans_laptop\indianajones.gif")
    esprites = LoadedSprite("C:\Users\Seans_laptop\\nazi.gif")
    g.start()
