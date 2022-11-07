import os
import argparse

#ignore_list = ['.DS_Store', '._*','*.jpg']

def sizeof_fmt(num, suffix="B"):
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"

def is_sys_file(name : str):
    return name == '.DS_Store' or name.startswith('._')

def is_to_consider(path : str):
    endswith = path.lower().endswith(('.jpg','.jpeg'))
    contains = 'RAW' in path
    contained = True
    #contained = 'RAW' in path.split(os.sep)

    return endswith and contains and contained

parser = argparse.ArgumentParser()

# Required positional argument
parser.add_argument('dir', type=str,
                    help='Folder')

args = parser.parse_args()

folder = args.dir

list = []

tot_count = 0
tot_ignored_count = 0
tot_sys_count = 0
tot_dir_size = 0

for dir, dirs, files in os.walk(folder):
    #for each directory
    
    count = 0
    ignored_count = 0
    sys_count = 0
    dir_size = 0

    for file_name in files:
        #for each file in the directory
        file_path = os.path.join(dir,file_name)

        if is_sys_file(file_name):
            sys_count += 1
            continue
        if not is_to_consider(file_path):
            ignored_count += 1
            continue
        
        count += 1

        sz = os.path.getsize(file_path)

        list.append((file_path,sz))

        dir_size += sz

    if count != 0:
        print('%s: %d files (%s), %d ignored, %d system' % (dir,count,sizeof_fmt(dir_size),ignored_count,sys_count)) #print(dir + ': ' + str(k) + ' files')

    tot_count += count
    tot_ignored_count += ignored_count
    tot_sys_count += sys_count
    tot_dir_size += dir_size

print('\nTOTAL: %d files (%s), %d ignored, %d system' % (tot_count,sizeof_fmt(tot_dir_size),tot_ignored_count,tot_sys_count)) #print(dir + ': ' + str(k) + ' files')

if count == 0:
    exit(0)

print('Do you wish to proceed? (y/n)')
answer = input().lower()

if answer != 'y':
    exit(0)


deleted_count = 0
deleted_size = 0
for (file_path,file_size) in list:
    print('%d/%d removed. Removing: %s'%(deleted_count,count,file_path), end='\x1b[K\r')
    try:
        os.remove(file_path)
    except Exception as error:
        print('error while removing file %s: %s' % (file_path,error))
        continue

    deleted_count += 1
    deleted_size += file_size

print('%d/%d file deleted. %s freed' % (deleted_count,count,sizeof_fmt(deleted_size)) ,end='\x1b[K\n')