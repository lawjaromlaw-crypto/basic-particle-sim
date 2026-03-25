from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ListProperty
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.properties import ReferenceListProperty
from kivy.properties import ObjectProperty
from random import randint
from kivy.uix.floatlayout import FloatLayout


    


class MassVariantParticle(Widget):

    mass = NumericProperty(0)
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)

    velocity = ReferenceListProperty(velocity_x, velocity_y)

    def move(self):
        self.pos = Vector(*self.velocity) + self.pos

    def reset_particle(self):
        self.pos = self.center
        self.velocity = Vector(4, 0).rotate(randint(0,360))

    def elastic_collide(self, other):
            
        dx = self.center_x - other.center_x
        dy = self.center_y - other.center_y

        distance = (dx**2 + dy**2)**.5
        min_dist = self.width/2 + other.width/2    #basically the radius of each ball added to find impact distance

        if 0 < distance < min_dist:
            # elastic collision, factors in mass difference
            v1 = Vector(self.velocity)
            v2 = Vector(other.velocity)
            
            new_v1 = ((self.mass - other.mass)*v1 + 2*other.mass*v2)/(self.mass+other.mass)
            new_v2 = ((other.mass - self.mass)*v2 + 2*self.mass*v1)/(other.mass+self.mass)

            self.velocity = list(new_v1)
            other.velocity = list(new_v2)

            #check overlap
            overlap = min_dist - distance
            nx, ny = dx / distance, dy / distance
            self.x += nx * overlap / 2
            self.y += ny * overlap / 2
            other.x -= nx * overlap / 2
            other.y -= ny * overlap / 2

class SpongyWallParticle(Widget):

    mass = NumericProperty(0)
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)


    velocity = ReferenceListProperty(velocity_x, velocity_y)

    def move(self):
        self.pos = self.pos

    def dampening_collide(self, other):
            
        dx = self.center_x - other.center_x
        dy = self.center_y - other.center_y

        distance = (dx**2 + dy**2)**.5
        min_dist = self.width/2 + other.width/2    #basically the radius of each ball added to find impact distance

        if 0 < distance < min_dist:
            # dampening sponge
            v2 = Vector(other.velocity)
            
            DAMPENING_FACTOR = 0.1
            
            new_v2 = DAMPENING_FACTOR*v2
            
            other.velocity = list(new_v2)

            #check overlap
            overlap = min_dist - distance
            nx, ny = dx / distance, dy / distance
            other.x -= nx * overlap
            other.y -= ny * overlap

#================================================================================

class TheCollisionExpert(MassVariantParticle, SpongyWallParticle):

    print("Hi, I'm the collision expert.")


#================================================================================
class ParticleSim(Widget):
    massballs = ListProperty([])
    spongeballs = ListProperty([])

    NUM_MASS_BALLS = 45
    NUM_SPONGE_BALLS = 1

    def set_particles(self):
        for massball in self.massballs:
            self.remove_widget(massball)
        self.massballs = []

        for spongeball in self.spongeballs:
            self.remove_widget(spongeball)
        self.spongeballs = []

        for i in range(self.NUM_MASS_BALLS):
            massball = MassVariantParticle()
            massball.center = self.center
            massball.pos = randint(0, 700), randint(0, 700)
            massball.velocity = Vector(4, 0).rotate(randint(0, 360))
            massball.mass = randint(1, 100)
            self.add_widget(massball)
            self.massballs.append(massball)

        for i in range(self.NUM_SPONGE_BALLS):
            spongeball = SpongyWallParticle()
            spongeball.center = self.center
            spongeball.pos = randint(0, 700), randint(0, 700)
            self.add_widget(spongeball)
            self.spongeballs.append(spongeball)

        

    def update(self, dt):
        for massball in self.massballs:
            massball.move()

            if massball.y < 0 or massball.top > self.height:
                massball.velocity_y *= -1

            if massball.x < 0 or massball.right > self.width:
                massball.velocity_x *= -1

        for spongeball in self.spongeballs:
            #ball.check_quadrant ???
            spongeball = spongeball


        for i in range(len(self.massballs)):
            for j in range(i+1, len(self.massballs)):
                self.massballs[i].elastic_collide(self.massballs[j])

        for i in range(len(self.spongeballs)):
            for j in range(i+1, len(self.spongeballs)):
                self.spongeballs[i].dampening_collide(self.spongeballs[j])

        for massball in self.massballs:
            for spongeball in self.spongeballs:
                spongeball.dampening_collide(massball)





class ParticleApp(App):
    
    def build(self):
        game = ParticleSim()
        game.set_particles()
        Clock.schedule_interval(game.update, 1.0/60.0)        

        return game
    

if __name__ == '__main__':
    ParticleApp().run()