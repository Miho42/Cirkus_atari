"""
Simple program to show moving a sprite with the keyboard.

This program uses the Arcade library found at http://arcade.academy

Artwork from https://kenney.nl/assets/space-shooter-redux

"""

import arcade
import arcade.color

# Import sprites from local file my_sprites.py
from my_sprites import Player, PlayerShot, Balloon, Wall

# Set the scaling of all sprites in the game
SPRITE_SCALING = 0.5

# Set the size of the screen
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Variables controlling the player
PLAYER_LIVES = 3
PLAYER_SPEED_X = 200
PLAYER_START_X = SCREEN_WIDTH / 2
PLAYER_START_Y = 50
PLAYER_SHOT_SPEED = 300

FIRE_KEY = arcade.key.SPACE

BALLOON_SPEED = 100
BALLOON_ROWS = 2
BALLOON_IN_ROW = 8

class GameView(arcade.View):
    """
    The view with the game itself
    """

    def on_show_view(self):
        """
        This is run once when we switch to this view
        """

        # Variable that will hold a list of shots fired by the player
        self.player_shot_list = arcade.SpriteList()

        # Variable that will hold lists of balloons
        self.balloon_list = []

        # List for walls
        self.walls = arcade.SpriteList()

        # List for emitters
        self.emitter_list = []

        # Set up the player info
        self.player_score = 0
        self.player_lives = PLAYER_LIVES

        # Create a Player object
        self.player = Player(
            center_x=PLAYER_START_X,
            center_y=PLAYER_START_Y,
            min_x_pos=0,
            max_x_pos=SCREEN_WIDTH,
            scale=SPRITE_SCALING,
        )

        # Create physics engine
        self.physics_engine = arcade.PymunkPhysicsEngine()

        # Create balloons
        self.set_up_balloons()

        # Create walls
        self.walls.append(self.make_wall(SCREEN_WIDTH/2, SCREEN_HEIGHT, SCREEN_WIDTH, 20))
        self.walls.append(self.make_wall(SCREEN_WIDTH/2, 0, SCREEN_WIDTH, 20))

        # Track the current state of what keys are pressed
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False

        # Get list of joysticks
        joysticks = arcade.get_joysticks()

        if joysticks:
            print("Found {} joystick(s)".format(len(joysticks)))

            # Use 1st joystick found
            self.joystick = joysticks[0]

            # Communicate with joystick
            self.joystick.open()

            # Map joysticks functions to local functions
            self.joystick.on_joybutton_press = self.on_joybutton_press
            self.joystick.on_joybutton_release = self.on_joybutton_release
            self.joystick.on_joyaxis_motion = self.on_joyaxis_motion
            self.joystick.on_joyhat_motion = self.on_joyhat_motion

        else:
            print("No joysticks found")
            self.joystick = None

        # Set the background color
        arcade.set_background_color(arcade.color.AMAZON)

    def set_up_balloons(self):
        """
        Adds desired number of balloons to list(s),
        and adds them to physics_engine
        """

        # Size of balloon
        balloon_width = 45
        balloon_height = 45

        balloon_max_x = SCREEN_WIDTH + balloon_width
        balloon_min_x = 0 - balloon_width

        # For flipping the direction of each row
        direction = 1

        # /4 because balloons takes up 1/4 of screen 
        spacing_height = (SCREEN_HEIGHT/4)/BALLOON_ROWS
        spacing_width = (SCREEN_WIDTH + 2 * balloon_width)/BALLOON_IN_ROW

        for row in range(BALLOON_ROWS):
            
            self.balloon_list.append(arcade.SpriteList())

            for b in range(BALLOON_IN_ROW):
                
                center_x = spacing_width * b
                center_y = (SCREEN_HEIGHT - spacing_height * row) - balloon_height

                if row % 2 == 1:
                    direction = -1

                new_balloon = Balloon(
                    center_x = center_x,
                    center_y = center_y,
                    max_pos_x = balloon_max_x,
                    min_pos_x = balloon_min_x,
                    width = balloon_width,
                    height = balloon_height
                )

                self.balloon_list[-1].append(new_balloon)

        for r in self.balloon_list:
            for b in r:
                self.physics_engine.add_sprite(
                    sprite = b,
                    elasticity=1,
                    gravity=(0,0),
                    collision_type="Balloon"
                )
                self.physics_engine.set_velocity(b, (BALLOON_SPEED * direction, 0))
            
            # Flip direction for next row
            direction *= -1 

    def make_wall(self, pos_x, pos_y, width, height):
        wall = Wall(
            pos_x,
            pos_y,
            width,
            height
        )

        self.physics_engine.add_sprite(
            sprite=wall,
            elasticity=1,
            body_type=arcade.PymunkPhysicsEngine.STATIC,
            collision_type="Wall"
            )
        
        return wall


    def flip_acrobat(self):
        """
        Flips the acrobat if needed
        """    
    
        for a in self.player_shot_list:
            # Get acrobat physics object
            acrobat_sprite = self.physics_engine.get_physics_object(a)
            # Get velocity og the acrobat physics object
            acrobat_velocity = acrobat_sprite.body.velocity

            if a.center_x > SCREEN_WIDTH or a.center_x < 0:
                self.physics_engine.set_velocity(a, (acrobat_velocity[0] * -1, acrobat_velocity[1]))

    def collision_acrobat_balloon(self, sprite_acrobat, sprite_balloon, arbiter, space, data):
        """
        Kill balloon in collision with acrobat
        """

        texture_blue = arcade.Texture.create_filled(
                name="explosion1",
                size=(20,20),
                color=arcade.color.BLUE_SAPPHIRE
            )
        
        texture_green = arcade.Texture.create_filled(
            name="explosion2",
            size=(5,5),
            color=arcade.color.GREEN,
        )
        
        emitter = arcade.make_burst_emitter(
            center_xy=(sprite_balloon.center_x, sprite_balloon.center_y),
            filenames_and_textures=[texture_green, texture_blue],
            particle_count=15,
            particle_speed=2,
            particle_lifetime_min=0.4,
            particle_lifetime_max=2,
        )
        self.emitter_list.append(emitter)
        sprite_balloon.kill()

    def collision_acrobat_wall(self, sprite_acrobat, sprite_balloon, arbiter, space, data):
        sprite_acrobat.life -= 1

        if sprite_acrobat.life < 1:
            sprite_acrobat.kill()

        

    def on_draw(self):
        """
        Render the screen.
        """

        # Clear screen so we can draw new stuff
        self.clear()

        # Draw the player shot
        self.player_shot_list.draw()

        # Draw the player sprite
        self.player.draw()

        # Draw balloons
        for ballon_row in self.balloon_list:
            ballon_row.draw()

        # Draw wall
        self.walls.draw()

        # Draw emitter(s)
        for e in self.emitter_list:
            e.draw()

        # Draw players score on screen
        arcade.draw_text(
            f"SCORE: {self.player_score}",  # Text to show
            10,  # X position
            SCREEN_HEIGHT - 20,  # Y positon
            arcade.color.WHITE,  # Color of text
        )

    def on_update(self, delta_time):
        """
        Movement and game logic
        """

        # Calculate player speed based on the keys pressed
        self.player.change_x = 0

        # Move player with keyboard
        if self.left_pressed and not self.right_pressed:
            self.player.change_x = -PLAYER_SPEED_X
        elif self.right_pressed and not self.left_pressed:
            self.player.change_x = PLAYER_SPEED_X

        # Move player with joystick if present
        if self.joystick:
            self.player.change_x = round(self.joystick.x) * PLAYER_SPEED_X

        # Update player sprite
        self.player.on_update(delta_time)

        # Update sprites
        self.physics_engine.step()

        # Flip arobat(s) if needed
        self.flip_acrobat()

        # Update emitters
        for e in self.emitter_list:
            e.update()

        # Check if balloons should wrap
        for r in self.balloon_list:
            for b in r:
                if (new_pos := b.wrap()) is not False:
                    self.physics_engine.set_position(b, new_pos)

        # Kill balloon if collision with acrobat
        self.physics_engine.add_collision_handler(
            first_type="Acrobat",
            second_type="Balloon",
            post_handler=self.collision_acrobat_balloon
        )

        self.physics_engine.add_collision_handler(
            first_type="Acrobat",
            second_type="Wall",
            post_handler=self.collision_acrobat_wall
        )


    def game_over(self):
        """
        Call this when the game is over
        """

        # Create a game over view
        game_over_view = GameOverView(score=self.player_score)

        # Change to game over view
        self.window.show_view(game_over_view)

    def on_key_press(self, key, modifiers):
        """
        Called whenever a key is pressed.
        """

        # End the game if the escape key is pressed
        if key == arcade.key.ESCAPE:
            self.game_over()

        # Track state of arrow keys
        if key == arcade.key.UP:
            self.up_pressed = True
        elif key == arcade.key.DOWN:
            self.down_pressed = True
        elif key == arcade.key.LEFT:
            self.left_pressed = True
        elif key == arcade.key.RIGHT:
            self.right_pressed = True

        if key == FIRE_KEY:
            # Player gets points for firing?
            self.player_score += 10

            # Create the new shot
            new_shot = PlayerShot(
                center_x=self.player.center_x,
                center_y=self.player.center_y,
                speed=PLAYER_SHOT_SPEED,
                max_y_pos=SCREEN_HEIGHT,
                scale=SPRITE_SCALING,
            )

            # Add the new shot to the list of shots
            self.player_shot_list.append(new_shot)

            # Add the new shot to physics engine
            self.physics_engine.add_sprite(
                sprite = new_shot,
                gravity=(0, -100),
                elasticity=0.9,
                collision_type="Acrobat"
                )
            # Speed added in y bc graphics are rotated
            self.physics_engine.set_velocity(new_shot, (0, PLAYER_SHOT_SPEED))


    def on_key_release(self, key, modifiers):
        """
        Called whenever a key is released.
        """

        if key == arcade.key.UP:
            self.up_pressed = False
        elif key == arcade.key.DOWN:
            self.down_pressed = False
        elif key == arcade.key.LEFT:
            self.left_pressed = False
        elif key == arcade.key.RIGHT:
            self.right_pressed = False

    def on_joybutton_press(self, joystick, button_no):
        print("Button pressed:", button_no)
        # Press the fire key
        self.on_key_press(FIRE_KEY, [])

    def on_joybutton_release(self, joystick, button_no):
        print("Button released:", button_no)

    def on_joyaxis_motion(self, joystick, axis, value):
        print("Joystick axis {}, value {}".format(axis, value))

    def on_joyhat_motion(self, joystick, hat_x, hat_y):
        print("Joystick hat ({}, {})".format(hat_x, hat_y))


class IntroView(arcade.View):
    """
    View to show instructions
    """

    def on_show_view(self):
        """
        This is run once when we switch to this view
        """

        # Set the background color
        arcade.set_background_color(arcade.csscolor.DARK_SLATE_BLUE)

        # Reset the viewport, necessary if we have a scrolling game and we need
        # to reset the viewport back to the start so we can see what we draw.
        arcade.set_viewport(0, self.window.width, 0, self.window.height)

    def on_draw(self):
        """
        Draw this view
        """
        self.clear()

        # Draw some text
        arcade.draw_text(
            "Instructions Screen",
            self.window.width / 2,
            self.window.height / 2,
            arcade.color.WHITE,
            font_size=50,
            anchor_x="center",
        )

        # Draw more text
        arcade.draw_text(
            "Press any key to start the game",
            self.window.width / 2,
            self.window.height / 2 - 75,
            arcade.color.WHITE,
            font_size=20,
            anchor_x="center",
        )

    def on_key_press(self, key: int, modifiers: int):
        """
        Start the game when any key is pressed
        """
        game_view = GameView()
        self.window.show_view(game_view)


class GameOverView(arcade.View):
    """
    View to show when the game is over
    """

    def __init__(self, score, window=None):
        """
        Create a Gaome Over view. Pass the final score to display.
        """
        self.score = score

        super().__init__(window)

    def setup_old(self, score: int):
        """
        Call this from the game so we can show the score.
        """
        self.score = score

    def on_show_view(self):
        """
        This is run once when we switch to this view
        """

        # Set the background color
        arcade.set_background_color(arcade.csscolor.DARK_GOLDENROD)

        # Reset the viewport, necessary if we have a scrolling game and we need
        # to reset the viewport back to the start so we can see what we draw.
        arcade.set_viewport(0, self.window.width, 0, self.window.height)

    def on_draw(self):
        """
        Draw this view
        """

        self.clear()

        # Draw some text
        arcade.draw_text(
            "Game over!",
            self.window.width / 2,
            self.window.height / 2,
            arcade.color.WHITE,
            font_size=50,
            anchor_x="center",
        )

        # Draw player's score
        arcade.draw_text(
            f"Your score: {self.score}",
            self.window.width / 2,
            self.window.height / 2 - 75,
            arcade.color.WHITE,
            font_size=20,
            anchor_x="center",
        )

    def on_key_press(self, key: int, modifiers: int):
        """
        Return to intro screen when any key is pressed
        """
        intro_view = IntroView()
        self.window.show_view(intro_view)


def main():
    """
    Main method
    """
    # Create a window to hold views
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT)

    # Game starts in the intro view
    start_view = IntroView()

    window.show_view(start_view)

    arcade.run()


if __name__ == "__main__":
    main()
