import argparse
import os
import shutil

parser = argparse.ArgumentParser(description='Optional app description')

# Required positional argument
parser.add_argument('source', type=str,
                    help='Source folder')

# Optional positional argument
parser.add_argument('dest', type=str,
                    help='Destination folder')

# Optional argument
parser.add_argument('--dry-run', action='store_true')

parser.add_argument('-v','--verbose', action='store_true')

parser.add_argument('-l','--list', action='store_true',
                    help='Just print a list of matching files')

parser.add_argument('-x','--extensions', action='append', help='List of extensions to match')


args = parser.parse_args()

if not os.path.isdir(args.source):
    print('source is not a valid directory')
    exit(-1)
if not os.path.isdir(args.dest):
    print('dest is not a valid directory')
    exit(-1)

def file_match(name):
    return (not name.startswith('._')) and name.lower().endswith(tuple(args.extensions))

copied_count = 0
skipped_count = 0

for root, dirs, files in os.walk(args.source):
   for name in files:
        if file_match(name):
            full_path = os.path.join(root, name)
            rel_path = os.path.relpath(full_path,args.source)
            if args.list:
                print(rel_path)
                continue
            dest_path = os.path.join(args.dest,rel_path)
            if args.verbose: print(rel_path + ' -> ' + dest_path)
            if not args.dry_run:
                shutil.copy2(args.source,dest_path)
            copied_count += 1
        else: skipped_count += 1

print(str(copied_count) + (' not' if args.dry_run else '') + ' copied. ')
print(str(skipped_count) + ' skipped. ')
