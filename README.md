# cardinal-pfl-analysis
A collection of data and scripts to try and figure out how much $CROWN the Cardinal treasury granted to each PFP and how much they were actually due.

# Directory Structure

## preview-website
A simple index.html page that when run (hosted locally with http.server or something because of CORS) allows you to easily query the output of the program. Relies on hardcoded 'output_with_rewards.json' in same directory 

## raw-cardinal-transactions
Initially zipped, but unzipped is a collection of JSON files from every single transaction taken by the Cardinal CROWN treasury wallet (FXSwRYKBwozWfCW4ya6M86NQ6QwikWPFZZhTqXnkV5es), organized by day. 

## raw-pfp-transactions
Initially zipped, but unzipped is a collection of JSON files from every single transaction assigned to every PFL PFP mint from August back to March.

## scripts
Collection of python scripts and helper / util CSV files that take that raw data and try to collate it into the final product used on the website.

# GIT LFS
Note, the zip files in this directory are somewhat large, therefore they are tracked via Git LFS, which means you'll need to install git LFS to make sure you get all the files. Details: https://git-lfs.com
