#!/usr/bin/env python

import os
import sys
import time
import matplotlib.pyplot as plt
from simple_pid import PID


class WaterBoiler:
    """
    Simple simulation of a water boiler which can heat up water
    and where the heat dissipates slowly over time.
    Change in heating is delayed by a fix number of cycles.
    """

    def __init__(self):
        self.water_temp = 45
        self.delayed_water_temp_changes = [0] * 30

    def update(self, boiler_power, dt):
        if boiler_power > 0:
            # Boiler can only produce heat, not cold
            self.delayed_water_temp_changes.append(10 * boiler_power * dt)
        else:
            self.delayed_water_temp_changes.append(0)
        
        self.water_temp += self.delayed_water_temp_changes.pop(0)
        if (self.water_temp > 100):
            self.water_temp = 100

        # Some heat dissipation
        self.water_temp -= self.water_temp * 0.05 * dt
        return round(self.water_temp, 1)


if __name__ == '__main__':
    boiler = WaterBoiler()
    water_temp = boiler.water_temp

    pid = PID(5, 0.1, 0.1, setpoint=water_temp)
    # pid = PID(0, 0.5, 0, Kpom=0.2, weightPom=None, setpoint=water_temp)
    pid.output_limits = (0, 300) # some power value of the heater

    start_time = time.time()
    last_time = start_time

    # Keep track of values for plotting
    setpoint, y, x = [], [], []

    while time.time() - start_time < 10:
        current_time = time.time()
        dt = current_time - last_time

        power = pid(water_temp)
        # print(pid.components)
        water_temp = boiler.update(power, dt)

        print(f"{(current_time - start_time):.3f} ({water_temp:.2f} {pid.setpoint:.2f}) ({power:.2f}) {pid.components}")

        x += [current_time - start_time]
        y += [water_temp]
        setpoint += [pid.setpoint]

        if current_time - start_time > 2:
            pid.setpoint = 50

        last_time = current_time

        time.sleep(0.005)

    plt.plot(x, y, label='measured')
    plt.plot(x, setpoint, label='target')
    plt.xlabel('time')
    plt.ylabel('temperature')
    plt.legend()
    if os.getenv('NO_DISPLAY'):
        # If run in CI the plot is saved to file instead of shown to the user
        plt.savefig(f"result-py{'.'.join([str(x) for x in sys.version_info[:2]])}.png")
    else:
        plt.show()
