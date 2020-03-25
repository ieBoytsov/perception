import os
from tempfile import TemporaryDirectory

import numpy as np

from src.core.visual_odometry.estimate_vehicle_trajectory import \
    EstimateVehicleTrajectory


def test_estimate_vehicle_trajectory_task():
    test_image_data_dir = (
        "/Users/i.boytsov/Projects/perception/tests/core/data/visual_odometry_data/"
    )
    dist_threshold = 0.6
    do_filter = True
    with TemporaryDirectory() as temp_dir:
        test_task = EstimateVehicleTrajectory(
            image_data_dir=test_image_data_dir,
            dest_dir=temp_dir,
            dist_threshold=dist_threshold,
            do_filter=do_filter,
        )
        test_task.execute()
        file_name = os.path.join(temp_dir, "trajectory.npy")
        assert len(os.listdir(temp_dir)) == 1
        assert os.path.exists(os.path.join(file_name))
        assert isinstance(np.load(file_name), np.ndarray)
