import os

import cv2
import numpy as np
import json


class ComputeDistanceToCollision:
    def __init__(self, depth_data_dir, masks_data_dir, dest_dir):
        super().__init__()
        self.depth_data_dir = depth_data_dir
        self.masks_data_dir = masks_data_dir
        self.dest_dir = dest_dir
        self.file_names = [x.split(".")[0] for x in os.listdir(self.depth_data_dir)]

    def class_mapping(self, obj_name):
        classes = [
            "Car",
            "Van",
            "Truck",
            "Pedestrian",
            "Person_sitting",
            "Cyclist",
            "Tram",
            "Misc",
            "DontCare",
        ]
        mapping = {}
        for idx, obj in enumerate(classes):
            mapping[obj] = idx

        return mapping[obj_name]

    def load_bboxes(self, mask_dir):

        with open(mask_dir) as f:
            content = f.readlines()
        content = [x.split() for x in content]
        content = [x for x in content if x[0] != "DontCare"]
        boxes = np.empty((len(content), 5), dtype=np.int)
        for idx, item in enumerate(content):
            y_min, x_min = int(float(item[4])), int(float(item[5]))
            y_max, x_max = int(float(item[6])), int(float(item[7]))

            boxes[idx, :] = [self.class_mapping(item[0]), x_min, y_min, x_max, y_max]

        return boxes

    def get_img_data(self, file_name):
        boxes = self.load_bboxes(os.path.join(self.masks_data_dir, file_name + ".txt"))
        depth_map = np.load(os.path.join(self.depth_data_dir, file_name + ".npy"))
        return boxes, depth_map

    def locate_obstacle_in_image(self, image, obstacle_image):

        # Run the template matching from OpenCV
        cross_corr_map = cv2.matchTemplate(image, obstacle_image, method=cv2.TM_CCOEFF)

        # Locate the position of the obstacle using the minMaxLoc function from OpenCV
        _, _, _, obstacle_location = cv2.minMaxLoc(cross_corr_map)

        return cross_corr_map, obstacle_location

    def get_distance_to_closest_object(self, detected_objects, depth_map):

        closest_point_depth = np.inf
        closest_object = None
        for bbox in detected_objects:
            detected_object, x_min, y_min, x_max, y_max = bbox
            obstacle_depth = depth_map[x_min:x_max, y_min:y_max]
            curr_point_depth = obstacle_depth.min()
            if curr_point_depth < closest_point_depth:
                closest_point_depth = curr_point_depth
                closest_object = detected_object
        return {str(closest_object): str(closest_point_depth)}

    def execute(self):
        for file_name in sorted(self.file_names):
            detected_objects, depth_map = self.get_img_data(file_name)
            object_distance_mapping = self.get_distance_to_closest_object(detected_objects, depth_map)
            with open(os.path.join(self.dest_dir, '{}.json'.format(file_name)), 'w') as fp:
                json.dump(object_distance_mapping, fp)