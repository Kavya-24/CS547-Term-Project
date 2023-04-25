# -*- coding: utf-8 -*-
"""Analysis-SWC-Contracts

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1sOeLkfu7CW-bgdc53F_7-KKNUwy55W0Z

##Preprocess dataset
"""

import os
import requests

api_url = "https://api.github.com/repos/{owner}/{repo}/contents/{path}"
owner = "smartbugs"
repo = "smartbugs-curated"

def download_content(node):
  content_url = node["download_url"]
  content_response = requests.get(content_url)
  file_path = f"downloaded_files/{node['path']}"

  # Check if the directory exists, and create it if it doesn't
  directory = os.path.dirname(file_path)
  if not os.path.exists(directory):
    os.makedirs(directory)
  
  if content_response.status_code == 200:
      with open(f"downloaded_files/{node['path']}", "wb") as f:
          f.write(content_response.content)
  else:
      print(f"Error downloading {node['path']}: {content_response.status_code}")

def traverse_tree(node):

  if node['type'] == 'dir':
    call_response(node['path'])
  else:
    if node["name"].endswith(".sol"):
      download_content(node)

def call_response(folder_path):

  url = api_url.format(owner=owner, repo=repo, path=folder_path)
  response = requests.get(url)

  if response.status_code == 200:
    os.makedirs("downloaded_files", exist_ok=True)
    for node in response.json():
      traverse_tree(node)
  else:
    print(f"Error listing files in folder: {response.status_code}")

  return

call_response("dataset")

folder_path = 'downloaded_files/dataset'
number_of_contracts = 0
contract_mapping = {}
contract_paths = []

for control in os.listdir(folder_path):
  control_folder_path = os.path.join(folder_path, control)
  
  for vulnerable_contract in os.listdir(control_folder_path):
    contract_path = os.path.join(control_folder_path, vulnerable_contract)
    contract_paths.append(contract_path)
    number_of_contracts += 1
    contract_mapping[vulnerable_contract] = control

print('Number of contracts: ' + str(number_of_contracts))

"""## Slither
Run and test out slither on 143 contracts
"""

#set up slither
!pip install slither-analyzer
!pip install solc-select
!solc-select install 0.4.24
import os
import subprocess
os.environ['SOLC_VERSION'] = '0.4.24'

# #analyse all the contracts using slither
print("\n=================Running Slither==========================\n")
slither_result = {}
for contract_path in contract_paths:
  try:
    p = "/content/" + contract_path
    result = subprocess.run(['slither', p], capture_output=True, text=True)
    slither_result[contract_path] = result.stderr
  except:
    print('unable to run slither for ' + contract_path)

# Open the file for writing
with open('slither_analysis_result.json', 'w') as f:
    # Convert the dictionary to JSON and write it to the file
    json.dump(slither_result, f)

"""## Mythril
Run and test out Mythrill on all the 143 contracts
"""

!pip install mythril

p = contract_paths[0]
result = subprocess.run(['myth','analyze', p], capture_output=True, text=True)
print(result)

# #analyse all the contracts using mythrill
print("\n\n\n\=================Running Mythrill==========================")
mythrill_result = {}
cnt = 0
for contract_path in contract_paths:
  cnt +=1
  print(cnt)

  try:
    p = contract_path
    result = subprocess.run(['myth','analyze', p], capture_output=True, text=True)
    mythrill_result[contract_path] = result.stdout
  except Exception as e:
    print(e)
    print('unable to run mythrill for ' + contract_path)

print(len(mythrill_result))

# # Open the file for writing
# with open('mythrill_analysis_run_10_result.json', 'w') as f:
#     # Convert the dictionary to JSON and write it to the file
#     json.dump(mythrill_result, f)



