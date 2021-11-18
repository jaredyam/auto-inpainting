import argparse
from pathlib import Path

import cv2

from utils import load_mask


def blend_image_and_mask(
        image_fpath,
        expand_mask=True,
        mask__color=(0.0, 0.6, 0.45),
        mask__opacity=0.4,
):
    image = cv2.imread(image_fpath)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)

    image_fpath = Path(image_fpath)
    mask_dir = Path('./data/masks_after_expansion' if expand_mask else './data/masks_after_segmentation')
    mask_fpath = mask_dir / (image_fpath.stem + ('_mask_after_expansion' if expand_mask else '_mask') + '.png')
    assert mask_fpath.is_file(), f'{mask_fpath} does not exist'

    binary_mask = load_mask(str(mask_fpath))
    bgra_mask = cv2.merge([binary_mask for _ in range(4)])
    bgra_mask[..., :3] = bgra_mask[..., :3] * mask__color[::-1]
    new_image = cv2.addWeighted(src1=image, alpha=1, src2=bgra_mask, beta=mask__opacity, gamma=0)

    outputs_dir = Path('./data/images_after_blending_with_mask')
    outputs_dir.mkdir(exist_ok=True)
    cv2.imwrite(
        str(outputs_dir / (image_fpath.stem + '_with_mask' + image_fpath.suffix)),
        new_image,
    )


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--image-fpath', type=str, required=True)
    parser.add_argument('--not-expand-mask', dest='expand_mask', action='store_false')
    parser.add_argument(
        '--mask-color',
        type=float,
        nargs=3,
        metavar=('red', 'green', 'blue'),
        default=(0.0, 0.6, 0.45),
    )
    parser.add_argument('--mask-opacity', type=float, default=0.4)
    args = parser.parse_args()

    blend_image_and_mask(
        args.image_fpath,
        expand_mask=args.expand_mask,
        mask__color=args.mask_color,
        mask__opacity=args.mask_opacity,
    )
