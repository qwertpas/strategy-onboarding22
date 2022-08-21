from datetime import timedelta
import time
from tkinter import E
import gym
from gym import spaces
from gym.utils.renderer import Renderer
import pygame
import numpy as np
from numpy import sin, cos
import json
from route import Route
from util import *

dir = os.path.dirname(__file__)

class RaceEnv(gym.Env):
    metadata = {
        "render_modes": ["human", "rgb_array", "single_rgb_array"], 
        "render_fps": 4
    }

    def __init__(self, render_mode="human", car="brizo_22fsgp", route="ind-gra_2022,7,9-10_10km"):

        with open(f"{dir}/cars/{car}.json", 'r') as props_json:
            self.car_props = json.load(props_json)
        
        route_obj = Route.open(route)
        self.legs = route_obj.leg_list
        self.total_length = route_obj.total_length

        self.leg_index = 0
        self.leg_progress = 0
        self.energy = 0
        self.time = self.legs[0]['start']
        self.miles_earned = 0
        self.target_speed = 0
        self.try_loop = False

        self.observation_spaces= spaces.Dict({
            "dist_traveled": spaces.Box(0, self.route.total_length),
            "slope": spaces.Box(-10, 10)
        })

        #action is setting the target speed and choosing whether to try loops
        self.action_space = spaces.Dict({
            "target_speed": spaces.Box(0, mpersec2mph(self.car_props['max_mph'])),
            "try_loop": spaces.Discrete(2),
        })


        assert render_mode is None or render_mode in self.metadata["render_modes"]
        self.render_mode = render_mode
        self._renderer = Renderer(self.render_mode, self._render_frame)

        self.window = None
        self.window_size = 512  # The size of the PyGame window
        self.clock = None

    def _get_obs(self):
        return {
            "agent": self._agent_location, 
            "target": self._target_location,
        }

    def reset(self, energy_budget=5400):
        # We need the following line to seed self.np_random
        super().reset()

        self.leg_index = 0
        self.time = self.legs[0]['start']
        self.energy = 0

        # Choose the agent's location uniformly at random
        self._agent_location = self.np_random.integers(0, self.size, size=2, dtype=int)

        # We will sample the target's location randomly until it does not coincide with the agent's location
        self._target_location = self._agent_location
        while np.array_equal(self._target_location, self._agent_location):
            self._target_location = self.np_random.integers(0, self.size, size=2, dtype=int)

        observation = self._get_obs()

        self._renderer.reset()
        self._renderer.render_step()

        return observation


    def charge(self, time_length:timedelta, tilted=True, updateTime=True):

        leg = self.legs[self.leg_index]


        end_time = self.time + time_length

        #array of charging times in seconds, spaced a minute apart
        np.arange(self.time.timestamp(), end_time.timestamp()+60, step=60) 

        leg['solar'](dist, )


        if updateTime: self.time += time_length

        self.energy += solar_func(self.leg_progress, self.time) * time_length


    def timing(self):

        '''
        Assumes the race always ends in a stage stop, and there are never 2 loops in a row.
        '''
        leg = self.legs[self.leg_index]

        if(self.leg_progress >= leg['length']):     #leg finished

            
            if(leg['end'] == 'checkpoint'):

                next_leg = self.legs[self.leg_index+1]

                if(self.time < leg['close']):       #on time
                    miles_earned += leg['length']

                    if(leg['type'] == 'loop'):
                        self.charge(timedelta(minutes=15))
                    else:
                        self.charge(timedelta(minutes=45))

                    if(self.time < leg['close']):    #there's time left until checkpoint closes

                        if(self.time < leg['open']):    #wait for checkpoint to open before moving on
                            self.charge(leg['open'] - self.time)
                            
                        if(self.try_loop and (leg['type']=='loop' or next_leg['type']=='loop')):
                            if(leg['type']=='loop'):
                                print('do the loop again at checkpoint')
                            else:
                                print('do the upcoming loop at checkpoint')
                                self.leg_index += 1
                        else:
                            self.charge(next_leg['start'] - self.time)
                            print('charge until next leg')

                    else:
                        self.charge(next_leg['start'] - self.time)
                        print('checkpoint closed, charge until next leg')

                else:   #arrived at checkpoint after it closed, move onto next base leg
                    if(next_leg['type']=='base'):
                        self.leg_index += 1
                        print('skipping checkpoint because arrived late')
                    else:
                        self.leg_index += 2     #next leg is a loop, skip it.
                        print('skipping checkpoint and loop because arrived late')

            else:   #this leg ends in a stagestop
                is_last_leg = self.leg_index == (len(self.legs) - 1)

                if(self.time < leg['close']):
                    miles_earned += leg['length']
                    self.charge(timedelta(minutes=15))






                            
                        





    def step(self, action):

        
        action['target_m/s']

        power_ff = v/K_m * (K_d*(v - w)^2) + K_f + K_g*sin(slope)
        accel = K_m * power_ext / v

        power_ext = accel * v / K_m

        power_total = power_ff + power_ext

        energy -= power_total

        


        done = np.array_equal(self._agent_location, self._target_location)

        reward = 1 if done else 0  # Binary sparse rewards

        observation = self._get_obs()
        info = self._get_info()

        self._renderer.render_step()

        return observation, reward, done, info

    def render(self):
        return self._renderer.get_renders()

    def _render_frame(self, mode):
        assert mode is not None

        if self.window is None and mode == "human":
            pygame.init()
            pygame.display.init()
            self.window = pygame.display.set_mode((self.window_size, self.window_size))
        if self.clock is None and mode == "human":
            self.clock = pygame.time.Clock()

        canvas = pygame.Surface((self.window_size, self.window_size))
        canvas.fill((255, 255, 255))
        pix_square_size = (
            self.window_size / self.size
        )  # The size of a single grid square in pixels

        # First we draw the target
        pygame.draw.rect(
            canvas,
            (255, 0, 0),
            pygame.Rect(
                pix_square_size * self._target_location,
                (pix_square_size, pix_square_size),
            ),
        )
        # Now we draw the agent
        pygame.draw.circle(
            canvas,
            (0, 0, 255),
            (self._agent_location + 0.5) * pix_square_size,
            pix_square_size / 3,
        )

        # Finally, add some gridlines
        for x in range(self.size + 1):
            pygame.draw.line(
                canvas,
                0,
                (0, pix_square_size * x),
                (self.window_size, pix_square_size * x),
                width=3,
            )
            pygame.draw.line(
                canvas,
                0,
                (pix_square_size * x, 0),
                (pix_square_size * x, self.window_size),
                width=3,
            )

        if mode == "human":
            # The following line copies our drawings from `canvas` to the visible window
            self.window.blit(canvas, canvas.get_rect())
            pygame.event.pump()
            pygame.display.update()

            # We need to ensure that human-rendering occurs at the predefined framerate.
            # The following line will automatically add a delay to keep the framerate stable.
            self.clock.tick(self.metadata["render_fps"])
        else:  # rgb_array
            return np.transpose(
                np.array(pygame.surfarray.pixels3d(canvas)), axes=(1, 0, 2)
            )

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

    def close(self):
        if self.window is not None:
            pygame.display.quit()
            pygame.quit()


def main():
    # env = GridWorldEnv()''

    env = RaceEnv(render_mode='human')

    obs = env.reset()


    while True:
        # Take a random action
        action = env.action_space.sample()
        obs, reward, done, info = env.step(action)
        
        # Render the game
        env.render()
        
        if done == True:
            break

    env.close()



if __name__ == "__main__":
    main()