import os
import glob
import clip
import torch
import pdb
from PIL import Image
from torchvision.datasets import CIFAR100

if __name__=="__main__":
    
    onlocal = False
    vocab = "data/things_classes.txt"   # imagenet21k_wordnet_lemmas.txt things_classes.txt
    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    if onlocal:
        imgdir = '/Users/katja/ownCloud/Share/roi_profiles'
    else:
        imgdir = '/LOCAL/kamue/big-spose-sleep/big_sleep'

    imgfns = glob.glob( os.path.join(imgdir, '*.png') )

    classes = []
    with open(vocab, 'r') as handle:
        lines = handle.readlines()
        for line in lines:
            classes.append( line.strip() )

    # debug: find max number of classes (must be processed in batches)
    classes = classes[:1200]

    model, preprocess = clip.load('ViT-B/32', device)   # TODO: replace with ViT-L/14

    text_inputs = torch.cat( [clip.tokenize(f"a photo of a {c}") for c in classes] ).to(device)
    text_features = model.encode_text(text_inputs)
    text_features /= text_features.norm(dim=-1, keepdim=True)

    classpredfile = open('classpredictions.txt', 'w')

    for imgfn in imgfns:
        image_input = preprocess( Image.open( os.path.join(imgdir, imgfn) ).convert("RGB") ).unsqueeze(0).to(device)

        # Calculate features
        with torch.no_grad():
            image_features = model.encode_image(image_input)

        # Pick the top 5 most similar labels for the image
        image_features /= image_features.norm(dim=-1, keepdim=True)
        similarity = (100.0 * image_features @ text_features.T).softmax(dim=-1)
        values, indices = similarity[0].topk(5)

        # Print the result
        print("\nTop predictions:\n")
        for value, index in zip(values, indices):
            print(f"{classes[index]:>16s}: {100 * value.item():.2f}%")

        classpredline = imgfn+": {} | {} | {} | {} | {}".format(topclasses)

        classpredfile.write('%s\n' % classpredline)
    
        break
    
    classpredfile.close()
    
