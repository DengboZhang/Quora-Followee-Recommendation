import os

def get_filepaths(directory):
    """
    This function will generate the file names in a directory
    tree by walking the tree either top-down or bottom-up. For each
    directory in the tree rooted at directory top (including top itself),
    it yields a 3-tuple (dirpath, dirnames, filenames).
    """
    file_paths = []  # List which will store all of the full filepaths.
    # Walk the tree.
    for root, directories, files in os.walk(directory):
        file_path1 = []
        for filename in files:
            p=root.split('/')[-1]
            print(p)
            x='/home/mukul/Desktop/IR/IR_Project/user_ques_Xt/'+p
            try:
                os.makedirs(x)

            except:
                print('path exist')
            #fp=open('"/home/mukul/Desktop/IR/IR_Project/user_ques_Xt/p/','a')
            #fp.close()
            # Join the two strings in order to form the full filepath.
            filepath = os.path.join(root, filename)
            file_path1.append(filepath) # Add it to the list.
        file_paths.append(file_path1)


    return file_paths  # Self-explanatory.

# Run the above function and store its results in a variable.
full_file_paths = get_filepaths("/home/mukul/Desktop/IR/IR_Project/quora_dataset")
print(full_file_paths)

'''
for root, directories, files in os.walk("C:\\Users\\Mukul\\Downloads\\users"):
    print(root)
    print(directories)
    print(files)
'''