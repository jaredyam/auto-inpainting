import argparse
from pathlib import Path

import cv2
import numpy as np
import pyclipper
from shapely.geometry import Polygon

from utils import load_mask


def expand_binary_mask(binary_mask, expand_ratio=0.5, polygon=False):
    assert all(np.unique(binary_mask) == [0, 255])

    expanded_paths = []

    contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        if polygon:
            epsilon = 0.01 * cv2.arcLength(contour, True)
            contour = cv2.approxPolyDP(contour, epsilon, True)
        points = contour.reshape(-1, 2)
        if len(points) < 3:
            continue
        poly = Polygon(points)
        distance = poly.area / poly.length * expand_ratio
        offset = pyclipper.PyclipperOffset()
        offset.AddPath(points, pyclipper.JT_ROUND, pyclipper.ET_CLOSEDPOLYGON)
        expanded_paths.extend([np.array(p) for p in offset.Execute(distance)])

    for p in expanded_paths:
        expanded_binary_mask = cv2.fillPoly(binary_mask, (p, ), (255, ))
    return expanded_binary_mask


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('mask_fpath', type=str)
    parser.add_argument('--expand-ratio', type=float, default=0.5)
    parser.add_argument('--polygon', action='store_true')
    args = parser.parse_args()

    binary_mask = load_mask(args.mask_fpath)
    expanded_binary_mask = expand_binary_mask(
        binary_mask,
        expand_ratio=args.expand_ratio,
        polygon=args.polygon,
    )

    mask_fpath = Path(args.mask_fpath).relative_to('.')
    outputs_dir = Path('./data/masks_after_expansion')
    outputs_dir.mkdir(exist_ok=True)
    expanded_mask_fpath = (outputs_dir /
                           f'{mask_fpath.stem}_after_expansion{mask_fpath.suffix}').relative_to('.')
    cv2.imwrite(str(expanded_mask_fpath), expanded_binary_mask)
    print(f'Successfully saved expanded mask of mask ({mask_fpath}) in: {expanded_mask_fpath}')
