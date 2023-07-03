import color_detection

if __name__ == "__main__":
    camera_subject = color_detection.CameraSubject('192.168.224.205', '8080')
    camera_subject.detect_dominant_color_continuously()