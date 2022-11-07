import argparse
import os
import shutil
import datetime

NFILES_PER_DIR = 999

def are_nested(folders):
    ppath = '@'
    for path in folders:
        if path.startswith(ppath): return True
        ppath = path
    return False

def camera_check(folders):
    for key,folder in folders.items():
        if len(folder.cameras) > 1:
            print('Found different cameras for the same folder %s: %s' % (key,folder.cameras))
            return False
    return True

def date_check(folders):
    # we assume it is already ordered by date
    for key,folders in folders.items():
        pmax = 0
        for folder in folders:
            if folder.date_min >= pmax:
                pmax = folder.date_max
            else:
                return False

    return True

def file_match(name,extensions):
    return (not name.startswith('._')) and name.lower().endswith(tuple(extensions))

def get_camera(name):
    return name[:4].upper()

def key_files(file):
    return file.date

def key_folders(item):
    return item.date_min

from dataclasses import dataclass,field

@dataclass
class Folder:
    path: str
    date_min: int = 0
    date_max: int = 0
    cameras: set = field(default_factory=set)
    files: list = field(default_factory=list)

@dataclass
class File:
    name: str
    path: str
    date: int
    camera: str

def main():
    parser = argparse.ArgumentParser(description='')


    parser.add_argument('source', type=str,
                        help='source folder')

    parser.add_argument('-y', '--yes', action='store_true', help='suppress confirmation prompt. Be aware!')

    parser.add_argument('-v','--verbose', action='store_true')

    parser.add_argument('-f','--flat-mode', action='store_true')

    parser.add_argument('-q','--quick', action='store_true', help='only scan `quick-samples` file per directory and bypass camera and date checks')
    parser.add_argument('-qs','--quick-samples', type=int, default=5, help='number of files picked per folder when --quick is specified')
    parser.add_argument('-x','--extensions', action='append', help='list of extensions to match in the form -x .ext1 -x .ext2')

    args = parser.parse_args()

    if args.quick and args.flat_mode:
        parser.error("--quick (-q) and --flat-mode (-f) are mutually exclusive. Please choose one")

    if (args.quick_samples != 5) and (args.quick is False):
        parser.error("--quick-samples requires --quick")

    if not os.path.isdir(args.source):
        print('error: source is not a valid directory')
        exit(-1)

    if args.quick:
        print('\nRunning in quick mode (-q) with %d samples per folder\n' % args.quick_samples)
    else:
        print('\nRunning in strict mode. Be patient\n')

    found_count = 0
    skipped_count = 0

    folders = {}

    for root, dirs, files in os.walk(args.source):
        qcount = 1
        for name in files:
            if file_match(name,args.extensions):
                full_path = os.path.join(root, name)
                rel_path = os.path.relpath(full_path,args.source)

                print('Scanning (%d scanned, %d ignored): %s'%(found_count,skipped_count,rel_path), end='\x1b[K\r')

                if not folders.get(root):
                    folders[root] = Folder(root)
                elif args.quick:
                    qcount += 1
                    if qcount > args.quick_samples:
                        break

                camera = get_camera(name)

                cr_time = os.stat(full_path).st_birthtime

                found_count += 1
                folders[root].files.append(File(name,full_path,cr_time,camera))

                # update folder
                folders[root].cameras.add(camera)
                folders[root].date_min = min(folders[root].date_min,cr_time)
                folders[root].date_max = max(folders[root].date_max,cr_time)

            else:
                skipped_count += 1

    print('Scanned %d files (%d ignored)' % (found_count,skipped_count),end='\x1b[K\n')

    

    if not args.flat_mode:
        if are_nested(folders):
            print('Folders are nested while running in directory mode. Exiting')
            exit(-1)

        if not camera_check(folders):
            print('Camera check failed while running in directory mode. Exiting')
            exit(-1)


        folders_by_camera = {}
        for key,folder in folders.items():
            camera = list(folder.cameras)[0]
            if not camera in folders_by_camera:
                folders_by_camera[camera]= []
            folders_by_camera[camera].append(folder)

        # sort folders by date
        for key,folders in folders_by_camera.items():
            folders = folders.sort(key=key_folders)

        if not args.quick and not date_check(folders_by_camera):
            print('Date check failed, can\'t help you')
            exit(-1)

        moves = []
        for key,folders in folders_by_camera.items():
            k = 1
            for folder in folders:
                new_name = key + '_' + str(k)
                new_path = os.path.join(args.source,new_name)
                if folder.path != new_path:
                    moves.append([folder.path,new_path])
                else: print('folder %s, already present' % folder.path)
                k += 1

        if not args.yes:
            print('\nFolders to move (%d):' % len(moves))
            for source,dest in moves:
                print('\t %s -> %s' % (os.path.relpath(source,args.source),os.path.relpath(dest,args.source)))
            print('\nDo you wish to proceed? ', end='')
            answer = input()
            if answer.lower() != 'y':
                exit(0)

        folders_moved_count = 0
        for source,dest in moves:
                print('Moving %s -> %s' % (source,dest))
                try:
                    os.rename(source, dest)
                    folders_moved_count += 1
                except Exception as error:
                    print('error while moving folder: %s' % error)
        print('%d folders moved' % folders_moved_count)

    else:
        # Flat mode (no directories)

        files_by_camera = {}
        for key,folder in folders.items():
            for file in folder.files:
                if not file.camera in files_by_camera:
                    files_by_camera[file.camera] = []
                files_by_camera[file.camera].append(file)

        for key,files in files_by_camera.items():
            n_files = len(files)
            print('%s: %d files -> %d folders' %(key,n_files,(n_files // NFILES_PER_DIR)+1))

        new_folders = {}
        copies = []
        for key,files in files_by_camera.items():
            
            # sort files by date
            #files = files.sort(key=key_files)
            folder_count = 1
            file_count = 1

            for file in files:
                if file_count == NFILES_PER_DIR +1:
                    folder_count += 1
                    file_count = 1

                new_folder = os.path.join(args.source,key + '_' + str(folder_count))
                #if not new_folder in new_folders:
                new_folders[new_folder] = file_count
        
                #if folder.path != new_folder:
                copies.append([file.path,new_folder])
                file_count += 1


        if not args.yes:
            print('\nFolders to create (%d):' % len(new_folders))
            for (folder,n) in new_folders.items():
                print('\t %s (%d)' % (folder,n))

            print('\nDo you wish to proceed? ', end='')
            answer = input()
            if answer.lower() != 'y':
                exit(0)


        '''for folder in new_folders:
                print('Creating %s' % folder)
                try:
                    os.mkdir(folder)
                except Exception as error:
                    print('error while creating folder: %s' % error)
        print('Folders created')

        for (source,dest) in copies:
                print('Copying %s -> %s' % (source,dest))
                try:
                    shutil.copy2(source,dest)
                except Exception as error:
                    print('error while copying file: %s' % error)'''

if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print('an unrecoverable error occured: %s' % error)
        exit(-1)
