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

    def has_parent(self):
        if not self.parents:
            return False
        else:
            return True

    def get_parents(self):
        return self.parents

    def get_children(self):
        return self.children


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

        parent_id = ""
        previous = ''
        parents_empty = False
        parent_stack = [head]
        commit_id = head


        while(not parents_empty):
            commit_id = parent_stack.pop()

            object_file_path = os.path.join(object_dir, commit_id[0:2], commit_id[2:])

            #add head to graph since its the first node
            if (commit_id not in graph):
                graph[commit_id] = CommitNode(commit_id)
            

            #navigate to object file path and decompress it
            with open (object_file_path, 'rb') as obj_file:
                compressed_file = obj_file.read()


            #read object to get id of parent commit
            object = zlib.decompress(compressed_file).decode("utf-8")
            parent_id = ""
            


            for line in object.splitlines():
                if line.startswith('parent'):
                    parent_id = line[7:]
                    parent_stack.append(parent_id)

            #add parent to the current commit
                    graph[commit_id].add_parent(parent_id)

            #build node for the parent
                    if parent_id not in graph:
                        graph[parent_id] = CommitNode(parent_id)
            #add the current commit as the child of the current parent
                    
                    graph[parent_id].add_child(commit_id)


            if not parent_stack:
                parents_empty = True

    return graph


def get_root_commits(graph):
    root_commits = []
    for commit in graph:
        if not graph[commit].has_parent():
            root_commits.append(commit)
    return root_commits


def generate_topo_order(graph):
    #children will represent the current children that need to be printed before the parents
    children = []
    topo_order = []
    #define a dictionary mapping to count the amount of children each parent has
    parents_countdown= dict()


    for commit in graph:
        #find all the commits in the graph without any children
        if not graph[commit].get_children():
            children.append(commit)

        #get the parents of each commit, and increment the childrent counts for each parent
        parents = graph[commit].get_parents()
        for parent in parents:
            if parent not in parents_countdown:
                parents_countdown[parent] = 1
            else:
                parents_countdown[parent] += 1


    x = 0

    #iterate through the list of children
    while x < len(children):
        child = children[x]
        parents = graph[child].get_parents()

    #add the children to the topological order
        topo_order.append(child)

    #decrement the children count for each parent of that child
        for parent in parents:
            parents_countdown[parent]-=1

            #if the parent has no more children, then the parent can be added to the print queue
            if parents_countdown[parent] == 0:
                children.append(parent)

        x+=1

    return topo_order

        


def main():
    graph = build_commit_graph()
    print(graph)
    print(get_root_commits(graph))
    print(generate_topo_order(graph))

if __name__ == "__main__":
    main()