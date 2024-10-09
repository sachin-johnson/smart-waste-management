# This script updates class labels for the consolidation of multiple datasets 
# in preparation for training with YOLO algorithms (.txt).

import os

# Class mapping for Zero Waste Dataset
class_mapping = {
    0: 2,
    1: 14,
    2: 11,
    3: 15,
    4: 8,
    5: 16
}

# Directories containing the label files
directories = ['train/labels', 'test/labels', 'valid/labels']

# Function to update the class labels in a file
def update_class_labels(file_path):
    updated_lines = []
    with open(file_path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            elements = line.strip().split()
            old_class = int(elements[0])
            if old_class in class_mapping:
                new_class = class_mapping[old_class]
                # Replace the old class with the new class
                elements[0] = str(new_class)
                updated_line = ' '.join(elements)
                updated_lines.append(updated_line)
            else:
                # If the class is not in the mapping, keep it unchanged
                updated_lines.append(line.strip())
    
    # Write the updated lines back to the file
    with open(file_path, 'w') as file:
        file.write('\n'.join(updated_lines) + '\n')

# Iterate through each directory and process the label files
for directory in directories:
    # Get the full path of the directory
    full_dir_path = os.path.join(os.getcwd(), directory)
    
    # Ensure the directory exists
    if not os.path.exists(full_dir_path):
        print(f"Directory {full_dir_path} does not exist, skipping...")
        continue
    
    # Loop through all label files in the directory
    for filename in os.listdir(full_dir_path):
        if filename.endswith('.txt'):
            file_path = os.path.join(full_dir_path, filename)
            print(f"Updating file: {file_path}")
            update_class_labels(file_path)

print("Class label update completed.")
