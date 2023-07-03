import cv2
import numpy as np
import webcolors
import serial
import time


class ColorObserver:
    def update(self, data):
        # Implement the logic to handle the updated data
        pass
    

class CameraSubject:
    def __init__(self, IP_ADDRESS: str, PORT_NUMBER: str):
        self.IP_ADDRESS = IP_ADDRESS
        self.PORT_NUMBER = PORT_NUMBER
        self.STREAM_URL = f"http://{self.IP_ADDRESS}:{self.PORT_NUMBER}/video"
        self.observers: list[ColorObserver] = []
        self.video_capture = cv2.VideoCapture(self.STREAM_URL)
        self.serial = serial.Serial('COM3', 9600)
        self.serial.write('0'.encode())
        self.last_color = ''
        
    
    def closest_colour(self, requested_colour):
        min_colours = {}
        for key, name in webcolors.CSS3_HEX_TO_NAMES.items():
            r_c, g_c, b_c = webcolors.hex_to_rgb(key)
            rd = (r_c - requested_colour[0]) ** 2
            gd = (g_c - requested_colour[1]) ** 2
            bd = (b_c - requested_colour[2]) ** 2
            min_colours[(rd + gd + bd)] = name
        return min_colours[min(min_colours.keys())]

    def get_colour_name(self, requested_colour):
        try:
            closest_name = actual_name = webcolors.rgb_to_name(requested_colour)
        except ValueError:
            closest_name = self.closest_colour(requested_colour)
            actual_name = None
        return actual_name, closest_name
        
    
    def detect_dominant_color_continuously(self):
        while True:
            # Read frame from the video stream
            ret, frame = self.video_capture.read()

            if ret:
                # Calculate the histogram for each channel
                histograms = []
                for i in range(3):
                    channel_hist = cv2.calcHist([frame], [i], None, [256], [0, 256])
                    histograms.append(channel_hist)

                # Find the index of the bin with the highest value in each histogram
                dominant_color_indexes = []
                for hist in histograms:
                    dominant_color_index = np.argmax(hist)
                    dominant_color_indexes.append(dominant_color_index)

                # Calculate the dominant color in BGR format
                dominant_color_bgr = np.array(dominant_color_indexes[::-1], dtype=np.uint8)

                try:
                    # Print the dominant color in BGR format
                    r = int(dominant_color_bgr[0])
                    g = int(dominant_color_bgr[1])
                    b = int(dominant_color_bgr[2])
                    rgb_tuple: webcolors.IntTuple = (r, g, b)
                    color_name = self.get_colour_name(rgb_tuple)[1]
                    # print(color_name)
                    # Verde
                    if color_name == 'seagreen' or color_name == 'mediumseangreen' or color_name == 'lightseangreen':
                        if self.last_color != 'Verde': 
                            print('Verde')
                            self.serial.write('300'.encode())
                            self.last_color = 'Verde'
                    # Amarillo
                    elif color_name == 'darkgoldenrod' or color_name == 'olive' or color_name == 'goldenrod':
                        if self.last_color != 'Amarillo':
                            print('Amarillo')
                            self.serial.write('360'.encode())
                            self.last_color = 'Amarillo'
                    # Azul
                    elif color_name == 'mediumturquoise' or color_name == 'steelblue' or color_name == 'cornflowerblue':
                        if self.last_color != 'Azul':
                            print('Azul')
                            self.serial.write('60'.encode())
                            self.last_color = 'Azul'
                    # Rojo
                    elif color_name == 'firebrick' or color_name == 'brown' or color_name == 'crimson' or color_name == 'tomato' or color_name == 'indianred':
                        if self.last_color != 'Rojo':
                            print('Rojo')
                            self.serial.write('90'.encode())
                            self.last_color = 'Rojo'
                except ValueError as error:
                    print(error)

                # Display dominant color on frame
                cv2.putText(frame, f"Dominant Color: {dominant_color_bgr}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

                # Display frame
                cv2.imshow("Video", frame)

                # Exit if 'q' key is pressed
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            else:
                break
    

    def register_observer(self, observer: ColorObserver):
        self.observers.append(observer)


    def unregister_observer(self, observer: ColorObserver):
        self.observers.remove(observer)


    def notify_observers(self, data: dict):
        for observer in self.observers:
            observer.update(data)