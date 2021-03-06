import os
import gc
import glob
import clip
import torch
import pdb
from PIL import Image
from torchvision.datasets import CIFAR100

def chunker(seq, size):
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))

if __name__=="__main__":
    
    onlocal = False
    vocab = "data/gpt3semantics.txt"
    # imagenet21k_wordnet_lemmas.txt things_classes.txt gpt3semantics.txt  TODO clip vocab?
    outfile = 'classpredictions.txt'
    n_batch = 750
    
    device = "cuda" if torch.cuda.is_available() else "cpu"

    if onlocal:
        imgdir = '/Users/katja/ownCloud/Share/roi_profiles'
        #imgdir = '/Users/katja/Documents/Data/THINGS/thingstestset'
    else:
        imgdir = '/LOCAL/kamue/thingstestset'
        #imgdir = '/LOCAL/kamue/big-spose-sleep/big_sleep'

    imgfns = []
    for imtype in ['*.jpg', '*.png']:
        imgfns += glob.glob( os.path.join(imgdir, imtype) )

    classes = []
    with open(vocab, 'r') as handle:
        lines = handle.readlines()
        for line in lines:
            classes.append( line.strip() )

    model, preprocess = clip.load('ViT-B/32', device)   # ViT-B/32 || ViT-L/14

    class_simils = { imgfn : torch.zeros([1,len(classes)]).to(device) for imgfn in imgfns }

    # collect class similarities
    cur_i = 0
    for classesbatch in chunker(classes, n_batch):

        text_inputs = torch.cat( [clip.tokenize(c) for c in classesbatch] ).to(device)
        text_features = model.encode_text(text_inputs)
        text_features /= text_features.norm(dim=-1, keepdim=True)  # TODO: norm across all?

        for imgfn in imgfns:
            image_input = preprocess( Image.open( os.path.join(imgdir, imgfn) ).convert("RGB") ).unsqueeze(0).to(device)

            # Calculate features
            with torch.no_grad():
                image_features = model.encode_image(image_input)

            # Pick the top 10 most similar labels for the imepdim=True)
            similarity = (100.0 * image_features @ text_features.T).softmax(dim=-1)
            class_simils[imgfn][ 0, cur_i:cur_i+len(classesbatch) ] = similarity.detach()

        cur_i += len(classesbatch)

        del text_features
        torch.cuda.empty_cache()


    # evaluate class similarities
    classpredfile = open(outfile, 'w')
    for imgfn in imgfns:
        
        # take top 15 classes
        vals, idxs = class_simils[imgfn][0].topk(15)   # auto-chooses last dimension

        classpredline = imgfn.split('/')[-1]
        for val, idx in zip(vals, idxs):
            classpredline += f",{100 * val.item():.2f}%|" + classes[idx]

        classpredfile.write('%s\n' % classpredline)
    
    classpredfile.close()
    
