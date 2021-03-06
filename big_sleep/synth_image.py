import os
os.environ['CUDA_VISIBLE_DEVICES']='0'
import fire
import random as rnd
from big_spose_sleep import Imagine
from pathlib import Path
import sys

def train(
    text=None,
    img=None,
    text_min="",
    spose=None,
    spose_to_clip_model="W_aridge_spose_to_clip.mat",  # xgb_spose_to_clip_defaultmodel.pkl", "xgb_spose_to_clip_defaultmodel.pkl"
    lr = .07,
    image_size = 512,
    gradient_accumulate_every = 1,
    epochs = 20,
    iterations = 1050,
    save_every = 50,
    overwrite = False,
    save_progress = False,
    save_date_time = False,
    bilinear = False,
    open_folder = True,
    seed = 0,
    append_seed = False,
    random = False,
    torch_deterministic = False,
    max_classes = None,
    class_temperature = 2.,
    save_best = False,
    experimental_resample = False,
    ema_decay = 0.5,
    num_cutouts = 128,
    center_bias = False,
):
    print(f'Starting up... ')

    if random:
        seed = rnd.randint(0, 1e6)

    imagine = Imagine(
        text=text,
        img=img,
        text_min=text_min,
        spose=spose, 
        spose_to_clip_model=spose_to_clip_model,
        lr = lr,
        image_size = image_size,
        gradient_accumulate_every = gradient_accumulate_every,
        epochs = epochs,
        iterations = iterations,
        save_every = save_every,
        save_progress = save_progress,
        bilinear = bilinear,
        seed = seed,
        append_seed = append_seed,
        torch_deterministic = torch_deterministic,
        open_folder = open_folder,
        max_classes = max_classes,
        class_temperature = class_temperature,
        save_date_time = save_date_time,
        save_best = save_best,
        experimental_resample = experimental_resample,
        ema_decay = ema_decay,
        num_cutouts = num_cutouts,
        center_bias = center_bias,
    )

    if not overwrite and imagine.filename.exists():
        answer = input('Imagined image already exists, do you want to overwrite? (y/n) ').lower()
        if answer not in ('yes', 'y'):
            exit()

    imagine()

if __name__=="__main__":

    spose = sys.argv[1] if len(sys.argv[1])>2 else int(sys.argv[1])
    train(spose=spose)
