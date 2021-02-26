import os 
import shutil

from trdg.generators import (
    GeneratorFromDict,
    GeneratorFromRandom,
    GeneratorFromStrings,
    GeneratorFromWikipedia,
)


def get_strings(file_name): 
    f = open(file_name, 'r')
    results = []
    for l in f.readlines():
        if l and l.strip():
            results.append(l.strip())
    return results
        

def get_fonts(font_dir):
    onlyfiles = [os.path.join(font_dir, f) for f in os.listdir(font_dir) if os.path.isfile(os.path.join(font_dir, f))]
    return onlyfiles
    


def get_training_data_img_and_labels(string_file, font_dir, output_folder, img_prefix, limit=1000): 
    strings = get_strings(string_file)
    fonts = get_fonts(font_dir)
    print(strings)
    print(fonts)
    generator = GeneratorFromStrings(
        strings,
        fonts = ['setofont/setofont.ttf'], 
#         blur=2,
#         random_blur=True
    )
    labels = [] 
    i = 0 
    for img, lbl in generator:
        if i<=limit: 
            file_name = os.path.join(output_folder, img_prefix, str(i)+".jpg")
            in_label_file_name = os.path.join(img_prefix, str(i)+".jpg")
            img.save(file_name)
            labels.append((in_label_file_name, lbl))
            i+=1 
        else: 
            break

    label_file = open(os.path.join(output_folder, "train.txt"), 'w')
    for l in labels: 
        line = '\t'.join(l)
        label_file.write(line)
        label_file.write('\n')


        
import sys 

## root directory of an output folder 
output_folder=sys.argv[1]
## image folder under root folder 
prefix = sys.argv[2]
## strings to be generated 
string_file = sys.argv[3]
## directories of fonts 
fonts_dir = sys.argv[4]
if os.path.exists(output_folder): 
    shutil.rmtree(output_folder)
os.mkdir(output_folder)
os.mkdir(os.path.join(output_folder, prefix))
get_training_data_img_and_labels(string_file, fonts_dir, output_folder, prefix)    






