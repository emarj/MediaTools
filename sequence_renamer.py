import os
import argparse

#ignore_list = ['.DS_Store', '._*','*.jpg']


def is_sys_file(name : str):
    return name == '.DS_Store' or name.startswith('._')

def is_to_consider(path : str):
    endswith = path.lower().endswith(('.jpg','.jpeg'))
    contains = ' ' in os.path.basename(path)
    contained = True
    #contained = 'RAW' in path.split(os.sep)

    return endswith and contains and contained

parser = argparse.ArgumentParser()

# Required positional argument
parser.add_argument('dir', type=str,
                    help='Folder')

args = parser.parse_args()

folder = args.dir

list = dict()

tot_count = 0
tot_ignored_count = 0
tot_sys_count = 0

for dir, dirs, files in os.walk(folder):
    #for each directory
    
    count = 0
    ignored_count = 0
    sys_count = 0

    for file_name in files:
        #for each file in the directory
        file_path = os.path.join(dir,file_name)

        if is_sys_file(file_name):
            sys_count += 1
            continue
        if not is_to_consider(file_path):
            ignored_count += 1
            continue
        
        

        (name,ext) = os.path.splitext(file_name)

        pos = name.rindex(' ')
        if len(name) - 1 - pos > 3:
            ignored_count += 1
            continue

        original_name = name[:pos] + ext

        if not os.path.exists(os.path.join(dir,original_name)):
            ignored_count += 1
            continue

        count += 1

        if not original_name in list:
            list[original_name] = []
            #list[original_name].append(original_name)
        
        list[original_name].append(file_name)

    tot_count += count
    tot_ignored_count += ignored_count
    tot_sys_count += sys_count

print('TOTAL: %d files, %d ignored, %d system' % (tot_count,tot_ignored_count,tot_sys_count)) #print(dir + ': ' + str(k) + ' files')

renames = []
for og_name in list:
    (name,ext) = os.path.splitext(og_name)
    new_name = name + ' 0' + ext
    print('%s -> %s' % (og_name,new_name))
    renames.append((og_name,new_name))

if count == 0:
    exit(0)

print('Do you wish to proceed? (y/n)')
answer = input().lower()

if answer != 'y':
    exit(0)

for (old,new) in renames:
    os.rename(os.path.join(folder,old),os.path.join(folder,new))