import os
import argparse
import subprocess

def sortKey(item):
    (filename,file_sz) = item
    return filename

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
    return path.lower().endswith(('.jpg','.jpeg','.py'))

parser = argparse.ArgumentParser()

# Required positional argument
parser.add_argument('dir', type=str,
                    help='Folder')

args = parser.parse_args()

folder = args.dir

list = []

count = 0
ignored_count = 0
dir_count = 0
sys_count = 0
dir_size = 0

#it = os.scandir(folder)
with os.scandir(folder) as it:
    for entry in it:
        file_name = entry.name
        file_path = os.path.join(folder,file_name)

        if not entry.is_file():
            dir_count += 1
            continue
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


print('%s: %d files (%s), %d ignored, %d system, %d directories' % (folder,count,sizeof_fmt(dir_size),ignored_count,sys_count,dir_count)) #print(dir + ': ' + str(k) + ' files')

if count == 0:
    exit(0)


list.sort(key=sortKey)

sep_list = []
zip_list = []

with open('./zipper.conf','r', encoding="utf-8") as file:
    while (line := file.readline().rstrip()):
        (sep,name) =  line.split(':')
        sep_list.append(sep.strip())
        zip_list.append(name.strip())


result = dict()
result_size = dict()
sep_index = 0
cur_zip_name = ''
for (file_path,file_sz) in list:
    if sep_index < len(sep_list) and os.path.basename(file_path) == sep_list[sep_index]:
        cur_zip_name = zip_list[sep_index]
        result[cur_zip_name] = []
        result_size[cur_zip_name] = 0
        sep_index += 1
    
    result[cur_zip_name].append(file_path)
    result_size[cur_zip_name] += file_sz


print(result)
print(result_size)
for (key,list) in result.items():
    print('%s.zip  :  %s -> %s' % (key,list[0],list[len(list)-1]))

for (key,list) in result.items():
    print('zip %s.zip %s' % (key,' '.join(list)))
    subprocess.run(['zip',key + '.zip'] +  list)