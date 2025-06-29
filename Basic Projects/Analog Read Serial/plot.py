from collections import deque
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import serial


SERIAL_PORT = 'COM5'
BAUD_RATE = 9600
sensor_min = 0
sensor_max = 1023


delay = 1
decay = 512


max_data_points = 1000
y_data = deque(maxlen = max_data_points)
y_data_decayed = deque(maxlen = max_data_points)
current_sum = 0
sum_of_weights = decay * (1 + decay) / 2


ser = serial.Serial(SERIAL_PORT, BAUD_RATE)
print(f"Connected to Arduino on {SERIAL_PORT} at {BAUD_RATE} baud.")
ser.flushInput()


fig, ax = plt.subplots()
line1, = ax.plot([], [], 'r-', label = 'Raw')
line2, = ax.plot([], [], 'g-', label = 'Decayed')


ax.set_ylim(sensor_min, sensor_max)
ax.set_xlim(0, max_data_points - 1)
ax.set_xlabel(f"Last {max_data_points} Readings")
ax.set_ylabel(f"Analog Sensor Value ({sensor_min} - {sensor_max})")
ax.set_title("Real - Time Sensor Data")
plt.grid(True)
plt.legend(loc = 'upper left')


y_data.extend([0] * max_data_points)
y_data_decayed.extend([0] * max_data_points)
x_data = list(range(max_data_points))


line1.set_data(x_data, list(y_data))
line2.set_data(x_data, list(y_data_decayed))


def update_animation(frame):
    global y_data, y_data_decayed, current_sum

    data = int(ser.readline().decode())
    y_data.append(data)


    # weighted_sum = 0
    # for i in range(decay):
    #     weighted_sum += y_data[- i - 1] * (decay - i)
    # weighted_sum /= sum_of_weights

    # This has been optimized below using some weird recursion due to the use of deque...


    current_sum += (y_data[-2] - y_data[-2 - decay])
    data_decay = y_data_decayed[-1] + 2 * y_data[-1] / (1 + decay) - current_sum / sum_of_weights

    y_data_decayed.append(data_decay)
    

    line1.set_ydata(list(y_data))
    line2.set_ydata(list(y_data_decayed))


    return line1, line2,


ani = animation.FuncAnimation(
    fig,
    update_animation,
    frames = None,
    interval = delay,
    blit = True,
    cache_frame_data = False
)
plt.show()