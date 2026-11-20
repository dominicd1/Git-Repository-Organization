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
            if file == ".DS_Store":
                continue
            branch_file_path = os.path.join(root, file)
            names.append(os.path.relpath(branch_file_path, target_dir))
    return names

class CommitNode:
    def __init__(self, commit_hash):
        """
        :type commit_hash: str
        """
        self.commit_hash = commit_hash
        self.parents = set()
        self.children = set()

    def add_child(self, commit_hash):
        self.children.add(commit_hash)

    def add_parent(self, commit_hash):
        self.parents.add(commit_hash)

    def get_parent(self):
        return self.parents



def build_commit_graph():
    branches = get_local_branch_names()
    git_dir = discover_git_dir()
    target_dir = os.path.join(git_dir, 'refs', 'heads')
    object_dir = os.path.join(git_dir, 'objects')

    #build a directed graph using a dictionary:

    graph = {}
    for branch in branches:
        branch_file_path = os.path.join(target_dir, branch)
        #open branch file path to read in commit id
        with open(branch_file_path, "r") as ref_file:
            head = ref_file.read().strip()
            

        #locate the object of commit
        #test

        commit_id = head
        parent_id = ""
        previous = ''
        parents_empty = False


        while(not parents_empty):
            object_file_path = os.path.join(object_dir, commit_id[0:2], commit_id[2:])

            graph[commit_id] = CommitNode(commit_id)
            
            #if there was a previous commit, then add that previous commit hash as a child
            if previous:
                graph[commit_id].add_child(previous)

            #navigate to object file path and decompress it
            with open (object_file_path, 'rb') as obj_file:
                compressed_file = obj_file.read()


            #read object to get id of parent commit
            object = zlib.decompress(compressed_file).decode("utf-8")
            parent_id = ""

            for line in object.splitlines():
                if line.startswith('parent'):
                    parent_id = line[7:]
                    graph[commit_id].add_parent(parent_id)


            previous = commit_id
            if parent_id:
                commit_id = parent_id
            else:
                parents_empty = True

    return graph


def get_root_commits(graph):
    root_commits = []
    for commit in graph:
        if not commit.get_parents():
            root_commits.append(commit)

def generate_topo_order():
    return 0

        


def main():
    graph = build_commit_graph()
    print(get_root_commits(graph))

if __name__ == "__main__":
    main()
