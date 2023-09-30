import math
import numpy as np
import cv2

class InputImage:
    def __init__(self, line_cnt, spl, depth, angle, radius, pixels):
        self.line_cnt = line_cnt  # number of lines scanned
        self.spl = spl            # number of sample points per line
        self.depth = depth        # scan depth
        self.angle = angle        # scanning angle
        self.radius = radius      # scan radius
        self.pixels = pixels      # image pixel data

class OutputImage:
    def __init__(self, width, height, pixels):
        self.width = width  # number of lines scanned
        self.height = height  # number of sample points per line
        self.pixels = pixels      # image pixel data

def convert_scan_image_w_nearest(raw):
    rad = math.radians(raw.angle)

    s_interval = raw.depth / (raw.spl - 1) # sampling interval [mm]
    a_interval = 2 * rad / (raw.line_cnt - 1) # angle interval [rad]
    R = raw.radius + raw.depth              # [mm]
    real_h = R - raw.radius * math.cos(rad) # [mm]
    real_w = 2 * R * math.sin(rad)          # [mm]
    center2top = raw.radius * math.cos(rad) # [mm]

    print(f"real size: {round(real_w, 2)} * {round(real_h, 2)} [mm]")

    # Create a OutputImage object 
    res_height = int(math.ceil(raw.spl * real_h / raw.depth)) # [pixels]
    res_width = int(math.ceil(res_height * real_w / real_h)) #  [pixels]
    res_pixels = np.zeros((res_height, res_width, 3), dtype=np.uint8)
    res = OutputImage(res_width, res_height, res_pixels)
    print(f"res size: {res_width} * {res_height} [pixels]")
    print(f"res.pixels.shape: {res.pixels.shape}")

    is_debug_loop = False 

    for i in range(res.height):
        real_y = center2top + i * s_interval  # real-world distance in y direction
        for j in range(res.width):
            if is_debug_loop:
                print(f"i: {i}, j: {j}")

            real_x = j * s_interval - real_w / 2  # real-world distance in x direction
            dist = math.sqrt(real_x ** 2 + real_y ** 2)
            theta = math.atan(real_x / real_y) #  [rad.] (-pi/2 ~ pi/2) 

            if is_debug_loop:
                print(f"dist: {round(dist, 2)} [mm], theta: {round(theta, 3)} [rad]")

            if -rad <= theta <= rad and raw.radius <= dist <= R:
                i_0 = int((dist - raw.radius) / s_interval)  # [pixels]
                j_0 = int((theta + rad) / a_interval) # [pixels]

                if is_debug_loop: 
                    print(f"i_0: {i_0}, j_0: {j_0}")           
              
                res.pixels[i, j] = raw.pixels[i_0][j_0]
            else:
                res.pixels[i, j] = [255, 0, 0]

                if is_debug_loop: 
                    print("* invalid theta or angle *")
            if is_debug_loop:
                print("------------------------------------------------")

    return res

# read raw image
image_path = "../images/input/input.jpeg"
img_data = cv2.imread(image_path) 

# get image's shape info 
original_height = img_data.shape[0] 
original_width = img_data.shape[1] 

# setup probe config
central_rad = 25.93 # [degrees]
half_central_rad = central_rad
d1_mm = 61.12 #  (depth start )[mm]

depth_mm = 80  # [mm]

input_img = InputImage(original_width, original_height, depth_mm, half_central_rad, d1_mm, img_data)
output_img = convert_scan_image_w_nearest(input_img)
cv2.imwrite("../images/output/output.png", output_img.pixels)

