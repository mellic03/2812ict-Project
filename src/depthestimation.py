

def pixel_dist_to_real_dist( d, p, k ) -> float:
    """
    Given a known real-world distance `d` and it's corresponding distance in pixels `p`,
    estimate the real-world distance corresponding to the pixel distance `k`.
    This assumes both objects are the same distance from the camera.
    """
    return (k / p) * d


def pixel_dist_to_real_depth( pixel_focal_length, pixel_dist, real_dist ) -> float:
    """Convert"""

    return (pixel_focal_length * real_dist) / pixel_dist
