import os
import shutil
import sys
import time
import logging
import filecmp

def log(log_path):
    logging.basicConfig(
        level=logging.INFO,
        encoding='utf-8',
        format='%(asctime)s - %(message)s',
        handlers=[
            logging.FileHandler(log_path),
            logging.StreamHandler()
        ]
    )

def dir_equal(dir1, dir2):
    dcmp = filecmp.dircmp(dir1, dir2)
    if dcmp.left_only or dcmp.right_only or dcmp.funny_files:
        return False
    for sub_dir in dcmp.common_dirs:
        if not dir_equal(os.path.join(dir1, sub_dir), os.path.join(dir2, sub_dir)):
            return False
    return True

def main(source_path, replica_path, sync_period):
    source_files = set(os.listdir(source_path))    
    replica_files = set(os.listdir(replica_path))
    remove_replica = replica_files.difference(source_files)
    
    for root, dirs, files in os.walk(source_path):
        rel_path = os.path.relpath(root, source_path)
        replica_root = os.path.join(replica_path, rel_path)

        for dir in dirs:
            source_dir = os.path.join(root, dir)
            replica_dir = os.path.join(replica_root, dir)
            
            if not os.path.exists(replica_dir):
                shutil.copytree(source_dir, replica_dir)
                logging.info("Directory created: " + replica_dir)
            elif not dir_equal(source_dir, replica_dir):
                shutil.rmtree(replica_dir)
                shutil.copytree(source_dir, replica_dir)
                logging.info("Directory updated: " + replica_dir)

        for file in files:
            source_file = os.path.join(root, file)
            replica_file = os.path.join(replica_root, file)

            if not os.path.exists(replica_file) or (os.path.getsize(source_file) != os.path.getsize(replica_file)):
                shutil.copy2(source_file, replica_file)
                logging.info("File created/updated: " + replica_file)

    for file in remove_replica:
        replica = os.path.join(replica_path, file)
        if os.path.isfile(replica):
            os.remove(replica)
            logging.info("File deleted: " +  replica)
        elif os.path.isdir(replica):
            shutil.rmtree(replica)
            logging.info("Directory deleted: " + replica) 

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Input in this order: python name.py source_path replica_path, synchronization_interval(in seconds), log_path")
        sys.exit(1)

    source_path = sys.argv[1]
    replica_path = sys.argv[2]  
    sync_period = int(sys.argv[3])  
    log_path = sys.argv[4]  

    log(log_path)
    while True:
        main(source_path, replica_path, sync_period)
        time.sleep(sync_period)
