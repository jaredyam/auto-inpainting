#!/usr/bin/env bash
set -euo pipefail

while [[ "$#" -gt 0 ]]; do
    case $1 in
    -i | --image-fpath)
        if [[ -f "$2" ]]; then
            __image_fpath="$2"
        else
            echo "Invalid image filepath: $2"
        fi
        shift
        ;;
    --expand-ratio)
        expand_ratio="$2"
        shift
        ;;
    *)
        echo "Unknown argument passed: $1"
        exit 1
        ;;
    esac
    shift
done
echo "Input image: $__image_fpath"

echo "Prepare input image..."
__image_fname=${__image_fpath##*/}
image_stem=${__image_fname%.*}
image_fpath="./data/images_before_segmentation/${image_stem}.png"
if [[ ! -f "$image_fpath" ]]; then
    cp -v "$__image_fpath" "$image_fpath"
fi

# Foreground segmentation
python ./segmentation-models/U-2-Net/u2net_test.py \
    --image-fpath="$image_fpath" \
    --prediction-dir="./data/masks_after_segmentation/" \
    --model-fpath="./segmentation-models/U-2-Net/saved_models/u2net/u2net.pth"

# Expand foreground mask
mask_fpath=$(find ./data/masks_after_segmentation -type f -name '*.png' | xargs ls -t | head -n 1)
python ./scripts/expand_mask.py "$mask_fpath" --expand-ratio="${expand_ratio-0.5}"
expanded_mask_fpath=$(find ./data/masks_after_expansion -type f -name '*.png' | xargs ls -t | head -n 1)

# Create temp directory for preparing inpainting model inputs
__temp_dir=$(mktemp -d)
trap "exit 1" HUP INT PIPE QUIT TERM
trap 'rm -rf "$__temp_dir"' EXIT
cp -v "$image_fpath" "$__temp_dir"
cp -v "$expanded_mask_fpath" "$__temp_dir"
# Inpainting (remove foreground)
export PYTHONPATH="$PWD/inpainting-models/lama"
python ./inpainting-models/lama/bin/predict.py \
    model.path="$PWD/inpainting-models/lama/big-lama" \
    indir="$__temp_dir" \
    outdir="$PWD/data/images_after_inpainting" \
    dataset.img_suffix=".png"
