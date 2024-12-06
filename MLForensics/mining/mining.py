### COMP-5710 Final Project ###
### 5c - Integrate forensics by modifying 5 Python methods of your choice. (20%)

import os
import pandas as pd 
import numpy as np
import csv 
import time 
from datetime import datetime
import subprocess
import shutil
from git import Repo
from git import exc 
import logging  # Importing the logging module

# Configure logging
logging.basicConfig(
    filename='mining.log',  # Log file name
    level=logging.INFO,     # Logging level
    format='%(asctime)s - %(levelname)s - %(message)s',  # Log message format
    datefmt='%Y-%m-%d %H:%M:%S'  # Date format
)

def giveTimeStamp():
    tsObj = time.time()
    strToret = datetime.fromtimestamp(tsObj).strftime('%Y-%m-%d %H:%M:%S')
    return strToret


def deleteRepo(dirName, type_):
    logging.info(f"Attempting to delete repository: {dirName} | Type: {type_}") # Method 1 for implementing forensics.
    print(':::' + type_ + ':::Deleting ', dirName)
    try:
        if os.path.exists(dirName):
            shutil.rmtree(dirName)
            logging.info(f"Successfully deleted repository: {dirName}")
        else:
            logging.warning(f"Directory does not exist: {dirName}")
    except OSError as e:
        logging.error(f"Error deleting repository {dirName}: {e}. Will try manually.")
        print('Failed deleting, will try manually')  


def dumpContentIntoFile(strP, fileP):
    logging.info(f"Dumping content into file: {fileP}") # Method 2 for implementing forensics.
    try:
        with open(fileP, 'w') as fileToWrite:
            fileToWrite.write(strP)
        file_size = os.stat(fileP).st_size
        logging.info(f"Successfully wrote to {fileP}. File size: {file_size} bytes")
        return str(file_size)
    except Exception as e:
        logging.error(f"Failed to write to file {fileP}: {e}")
        raise


def makeChunks(the_list, size_):
    for i in range(0, len(the_list), size_):
        yield the_list[i:i+size_]


def cloneRepo(repo_name, target_dir):
    logging.info(f"Cloning repository: {repo_name} into {target_dir}") # Method 3 for implementing forensics.
    cmd_ = f"git clone {repo_name} {target_dir}"
    try:
        subprocess.check_output(['bash','-c', cmd_])    
        logging.info(f"Successfully cloned repository: {repo_name} into {target_dir}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to clone repository {repo_name}: {e}")
        print('Skipping this repo ... trouble cloning repo:', repo_name )


def checkPythonFile(path2dir): 
    usageCount = 0
    patternDict = ['sklearn', 'h5py', 'gym', 'rl', 'tensorflow', 'keras', 'tf', 'stable_baselines', 'tensorforce', 'rl_coach', 'pyqlearning', 'MAMEToolkit', 'chainer', 'torch', 'chainerrl']
    for root_, dirnames, filenames in os.walk(path2dir):
        for file_ in filenames:
            full_path_file = os.path.join(root_, file_) 
            if(os.path.exists(full_path_file)):
                if ((file_.endswith('py')) or (file_.endswith('ipynb')))  :
                    try:
                        with open(full_path_file, 'r', encoding='latin-1') as f:
                            pythonFileContent = f.read()
                        pythonFileContent = pythonFileContent.split('\n') 
                        pythonFileContent = [z_.lower() for z_ in pythonFileContent if z_!='\n' ]
                        for content_ in pythonFileContent:
                            for item_ in patternDict:
                                if(item_ in content_):
                                    usageCount += 1
                                    print('item_->->->',  content_)  
                                    logging.debug(f"Pattern '{item_}' found in file {full_path_file}")                  
                    except Exception as e:
                        logging.error(f"Error reading file {full_path_file}: {e}")
    return usageCount  


def days_between(d1_, d2_):  # pass in date time objects, if string see commented code 
    # d1_ = datetime.strptime(d1_, "%Y-%m-%d")
    # d2_ = datetime.strptime(d2_, "%Y-%m-%d")
    return abs((d2_ - d1_).days)


def getDevEmailForCommit(repo_path_param, hash_):
    author_emails = []

    cdCommand         = "cd " + repo_path_param + " ; "
    commitCountCmd    = " git log --format='%ae'" + hash_ + "^!"
    command2Run = cdCommand + commitCountCmd

    try:
        author_emails = str(subprocess.check_output(['bash','-c', command2Run]))
        logging.info(f"Retrieved author emails for commit {hash_} in repo {repo_path_param}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to get developer emails for commit {hash_}: {e}")

    author_emails = author_emails.split('\n')
    # print(type(author_emails)) 
    author_emails = [x_.replace(hash_, '') for x_ in author_emails if x_ != '\n' and '@' in x_ ] 
    author_emails = [x_.replace('^', '') for x_ in author_emails if x_ != '\n' and '@' in x_ ] 
    author_emails = [x_.replace('!', '') for x_ in author_emails if x_ != '\n' and '@' in x_ ] 
    author_emails = [x_.replace('\\n', ',') for x_ in author_emails if x_ != '\n' and '@' in x_ ] 
    try:
        author_emails = author_emails[0].split(',')
        author_emails = [x_ for x_ in author_emails if len(x_) > 3 ] 
        # print(author_emails) 
        author_emails = list(np.unique(author_emails) )
    except IndexError as e_:
        logging.warning(f"No author emails found for commit {hash_}: {e_}")
        pass
    return author_emails  


def getDevDayCount(full_path_to_repo, branchName='master', explore=1000):
    logging.info(f"Calculating developer day count for repo: {full_path_to_repo} on branch: {branchName}") # Method 4 for implementing forensics.
    repo_emails = []
    all_commits = []
    repo_emails = []
    all_time_list = []
    if os.path.exists(full_path_to_repo):
        try:
            repo_  = Repo(full_path_to_repo)
            all_commits = list(repo_.iter_commits(branchName))   
            logging.info(f"Total commits found: {len(all_commits)}")
        except exc.GitCommandError as e:
            logging.error(f"Git command error for repo {full_path_to_repo}: {e}")
            print('Skipping this repo ... due to branch name problem', full_path_to_repo )
            return 0, 0, 0, 0

        # only check commit by commit if less than explore threshold
        for commit_ in all_commits[:explore]:
            commit_hash = commit_.hexsha

            emails = getDevEmailForCommit(full_path_to_repo, commit_hash)
            repo_emails += emails

            timestamp_commit = commit_.committed_datetime
            str_time_commit  = timestamp_commit.strftime('%Y-%m-%d')  # date with time 
            all_time_list.append(str_time_commit)

    all_day_list = [datetime(int(x_.split('-')[0]), int(x_.split('-')[1]), int(x_.split('-')[2]), 12, 30) for x_ in all_time_list]
    try:
        min_day        = min(all_day_list) 
        max_day        = max(all_day_list) 
        ds_life_days   = days_between(min_day, max_day)
        logging.info(f"Repository age: {ds_life_days} days")
    except (ValueError, TypeError) as e:
        logging.warning(f"Error calculating repository age for {full_path_to_repo}: {e}")
        ds_life_days   = 0
    ds_life_months = round(float(ds_life_days)/float(30), 5)

    dev_count = len(repo_emails)
    commit_count = len(all_commits)
    logging.info(f"Developers: {dev_count}, Commits: {commit_count}, Age (days): {ds_life_days}, Age (months): {ds_life_months}")
    return dev_count, commit_count, ds_life_days, ds_life_months 


def getPythonFileCount(path2dir):
    valid_list = [] 
    for _, _, filenames in os.walk(path2dir):
        for file_ in filenames:
            if ((file_.endswith('py')) or (file_.endswith('ipynb'))):
                valid_list.append(file_)
    return len(valid_list)   


def cloneRepos(repo_list, dev_threshold=3, python_threshold=0.10, commit_threshold = 25): 
    logging.info("Starting the cloning of repositories.") # Method 5 for implementing forensics.
    counter = 0     
    str_ = ''
    all_list = []
    for repo_batch in repo_list:
        for repo_ in repo_batch:
            counter += 1 
            logging.info(f"Processing repository {counter}: {repo_}")
            print('Cloning ', repo_ )
            dirName = '../FSE2021_REPOS/' + repo_.split('/')[-2] + '@' + repo_.split('/')[-1]  # '/' at the end messes up the index 
            cloneRepo(repo_, dirName )
            ### get all count 
            checkPattern, dev_count, python_count, commit_count, age_months   = 0 , 0, 0, 0, 0 
            flag = True
            all_fil_cnt = sum([len(files) for r_, d_, files in os.walk(dirName)])
            python_count = getPythonFileCount(dirName) 
            if (all_fil_cnt <= 0):
                deleteRepo(dirName, 'NO_FILES')
                flag = False
                logging.warning(f"Repository {dirName} has no files.")
            elif (python_count < (all_fil_cnt * python_threshold) ):
                deleteRepo(dirName, 'NOT_ENOUGH_PYTHON_FILES')
                flag = False
                logging.warning(f"Repository {dirName} does not have enough Python files.")
            else:       
                dev_count, commit_count, age_days, age_months  = getDevDayCount(dirName)
                if (dev_count < dev_threshold):                
                    deleteRepo(dirName, 'LIMITED_DEVS') 
                    flag = False  
                    logging.warning(f"Repository {dirName} has limited developers: {dev_count}")
                elif (commit_count < commit_threshold):                
                    deleteRepo(dirName, 'LIMITED_COMMITS')  
                    flag = False
                    logging.warning(f"Repository {dirName} has limited commits: {commit_count}")
            if (flag == True): 
                checkPattern = checkPythonFile(dirName) 
                if (checkPattern == 0 ):
                    deleteRepo(dirName, 'NO_PATTERN')
                    flag = False        
                    logging.warning(f"Repository {dirName} does not match any patterns.")
            print('#'*100 )
            str_ = str_ + f"{counter},{repo_},{dirName},{checkPattern},{dev_count},{flag},\n"
            tup = ( counter,  dirName, dev_count, all_fil_cnt, python_count , commit_count, age_months, flag)
            all_list.append(tup) 
            logging.info(f"So far we have processed {counter} repos.")
            print("So far we have processed {} repos".format(counter) )
            if((counter % 100) == 0):
                dumpContentIntoFile(str_, 'tracker_completed_repos.csv')
                df_ = pd.DataFrame(all_list) 
                df_.to_csv('PYTHON_BREAKDOWN.csv', header=['INDEX', 'REPO', 'DEVS', 'FILES', 'PYTHON_FILES', 'COMMITS', 'AGE_MONTHS', 'FLAG'], index=False, encoding='utf-8')    
                logging.info(f"Checkpoint: {counter} repositories processed.")

            if((counter % 1000) == 0):
                logging.info(f"Milestone reached: {counter} repositories.")
                print(str_)                
            print('#'*100)
        print('*'*10)
    
    logging.info("Completed cloning all repositories.")


if __name__=='__main__':
    logging.info("Script started.")
    repos_df = pd.read_csv('security_vulnerability_report.csv', sep='delimiter')
    logging.info("Loaded repository list from security_vulnerability_report.csv")
    print(repos_df.head())
    list_    = repos_df['url'].tolist()
    list_ = np.unique(list_)
    
    t1 = time.time()
    logging.info(f"Started processing at: {giveTimeStamp()}")
    print('Started at:', giveTimeStamp() )
    print('*'*100 )
    
    print('Repos to download:', len(list_)) 
    ## need to create chunks as too many repos 
    chunked_list = list(makeChunks(list_, 100))  ### list of lists, at each batch download 1000 repos 
    cloneRepos(chunked_list)
    
    print('*'*100 )
    print('Ended at:', giveTimeStamp() )
    print('*'*100 )
    t2 = time.time()
    time_diff = round( (t2 - t1 ) / 60, 5) 
    print('Duration: {} minutes'.format(time_diff) )
    print( '*'*100  )
    logging.info(f"Ended processing at: {giveTimeStamp()}")
    logging.info(f"Total duration: {time_diff} minutes")