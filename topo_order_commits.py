import os, zlib, sys



def discover_git_dir():
    current = os.getcwd()
    #loop until directory == .git

    
    while True:
        directory_path = os.path.join (current, '.git')
        #check if its an existing directory 
        if (os.path.isdir(directory_path)):
            return directory_path


        #otherwise, strip off the git --> remove .git
        directory_path = os.path.dirname(directory_path)
        #now, move up one directory from original
        parent_dir = os.path.dirname(directory_path)

        #if you reach the root without detecting it, you're not in a git repository
        if (parent_dir == directory_path):
            sys.stderr.write("Not inside a Git repository")
            sys.exit(1)
        else:
            directory_path = parent_dir

def get_local_branch_names():
    names = []
    git_dir = discover_git_dir()
    target_dir = os.path.join(git_dir, 'refs', 'heads')

    #walk through directory and get the relative filepath for each branch
    for root, dir, files in os.walk(target_dir):
        for file in files:
            branch_file_path = os.path.join(root, file)
            names.append(os.path.relpath(branch_file_path, target_dir))
    return names


def main():
    print(get_local_branch_names())

if __name__ == "__main__":
    main()