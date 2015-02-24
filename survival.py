from Tkinter import *
from math import cos,radians,sin,atan2,degrees,pi
from random import randint
class Game:
    def __init__(self):
        self.pressed = {}
        self.bullets = []
        self.enemies = []
        self._create_ui()
        self.pause = False
        self.kills = 0
        self.spawn = 1.0

    def start(self):
        self._animate()
        self.root.mainloop()

    def _create_ui(self):
        self.root = Tk()
        self.canvas = Canvas(width=500,height=500)
        self.canvas.pack()
        self.player = Player(self.canvas,x=250,y=250)
        self._set_bindings()
    
    def _animate(self):
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
                self.root.unbind("<ButtonPress-1>")
                self.root.unbind("<ButtonPress-3>")
                self.root.unbind("<Enter>")
                self.root.unbind("<Leave>")
                self.root.unbind("<space>")
                return False
            e.redraw()

        for b in self.bullets:
            
            if ( 0 <= b.x1 <= 500 and 0 <= b.y1 <= 500):
                for e in self.enemies:
                    if e.contains_point(b.x1,b.y1):
                        e.hurt(b.dmg)
                        b.hit = True
                if b.hit:
                    self.canvas.delete(b.img)
                    self.bullets.remove(b)
                else:
                    b.redraw()
            else:
                self.canvas.delete(b.img)
                self.bullets.remove(b)

        self.root.after(2,self._paused)

    def _paused(self):
        if self.pause:
            self.root.after(2,self._paused)
        else:
            self.root.after(48,self._animate)

    def _change_pause(self,event):
        if event.type == '8':
            self.pause = True
        elif event.type == '7':
            self.pause = False
        elif event.type == "2":
            if self.pause == False:
                self.pause = True
            else:
                self.pause = False

    def _add_enemy(self,event=None,x=None,y=None):
        if event == None:
            self.enemies.append(Enemy(self.canvas,x=x,y=y))
        else:
            self.enemies.append(Enemy(self.canvas,x=event.x,y=event.y))

    def _set_bindings(self):
        for char in "wasd":
            self.root.bind("<KeyPress-{}>".format(char),self._pressed)
            self.root.bind("<KeyRelease-{}>".format(char),self._released)
            self.pressed[char] = False
#        self.root.bind("<B1-Motion>",self._shoot)
        self.root.bind("<ButtonPress-1>", self._shoot)
        self.root.bind("<ButtonPress-3>", self._add_enemy)
        self.root.bind("<Enter>", self._change_pause)
        self.root.bind("<Leave>", self._change_pause)
        self.root.bind("<space>", self._change_pause)

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
    def __init__(self,canvas,startx,startx,clickx,clicky):
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
        self.spritesheet = PhotoImage(file=".\images\\nazi.gif")
        self.sprites = {}
        self.sprite_direction = "down"
        self.sprite_frame = 0
        self._sprites()
        self.img =  self.canvas.create_image(self.x,self.y,image=self.sprites[self.sprite_direction][self.sprite_frame])

    def _subimage(self,src,l,t,r,b):
        dst = PhotoImage()
        dst.tk.call(dst,'copy', src, '-from',l,t,r,b,'-to',0,0)
        return dst

    def _sprites(self):
        for d,row in zip(['down','left','right','up'],xrange(4)):
            for col in xrange(4):
                if not self.sprites.get(d):
                    self.sprites[d] = []
                self.sprites[d].append(self._subimage(self.spritesheet,32*col,48*row,32*(col+1),48*(row+1)))


    def contains_point(self,x,y):
        try:
            l,t,r,b = self.canvas.bbox(self.img)
        except TypeError:
            return False
        if l <= x <= r and t <= y <= b:
            return True
        else:
            return False

    def hurt(self,dmg):
        self.hp -= dmg
        if self.hp <= 0:
            g.enemies.remove(self)
            g.kills += 1
            g.spawn += 0.2
            self.canvas.delete(self.img)
            for _ in xrange(int(g.spawn)):
                g._add_enemy(x=randint(0,500),y=randint(0,500))
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
        #print "{} {}\n{} {}\n-------------".format(self.x,self.y,change_x,change_y)
        self.x += change_x
        self.y += change_y
        self.img = self.canvas.create_image(self.x,self.y,image=self.sprites[self.sprite_direction][self.sprite_frame])
        self.sprite_frame = (self.sprite_frame+1)%4


class Player:
    def __init__(self,canvas,x,y):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.spritesheet = PhotoImage(file=".\images\indianajones.gif")
        self.sprites = {}
        self.sprite_direction = "down"
        self.sprite_frame = 0
        self._sprites()
        self.speed = 6
        self.img = self.canvas.create_image(self.x,self.y,image=self.sprites[self.sprite_direction][self.sprite_frame])
        
        self.redraw()

    def _subimage(self,src,l,t,r,b):
        dst = PhotoImage()
        dst.tk.call(dst,'copy', src, '-from',l,t,r,b,'-to',0,0)
        return dst

    def _sprites(self):
        for d,row in zip(['down','left','right','up'],xrange(4)):
            for col in xrange(4):
                if not self.sprites.get(d):
                    self.sprites[d] = []
                self.sprites[d].append(self._subimage(self.spritesheet,32*col,48*row,32*(col+1),48*(row+1)))

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

if __name__ == "__main__":
    g = Game()
    g.start()
