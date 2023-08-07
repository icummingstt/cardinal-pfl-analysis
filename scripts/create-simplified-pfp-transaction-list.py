import json
import datetime
import pandas as pd
import os

def process_directory(directory_path):
    # Initialize list to store the rows of the CSV
    csv_rows = []
    seen_signatures = set()

    # Iterate over all the JSON files in the directory
    for filename in os.listdir(directory_path):
        if filename.endswith(".json"):
            file_path = os.path.join(directory_path, filename)

            # Open and load the JSON file
            with open(file_path) as file:
                data = json.load(file)

            # Get the mint address from the file name by removing the '.json'
            mint_address = os.path.basename(file_path).replace('.json', '')

            # Iterate over all the events in the data
            for event in data:
                # Check if the 'meta' field exists in the event
                if 'meta' in event:
                    # Initialize row with date in Column A
                    date = datetime.datetime.utcfromtimestamp(event['blockTime']).strftime('%-m/%-d/%Y %-I:%M%p')
                    row = {'Date': date}

                    # signature
                    signature = event['transaction']['signatures'][0]

                    # Initialize an empty list to store instructions
                    instructions = []

                    # Loop over log messages
                    for message in event['meta'].get('logMessages', []):
                        # Check if the message is an instruction
                        if 'Program log: Instruction:' in message:
                            # Append the instruction to the list
                            instructions.append(message.split(': ')[-1])

                    # Join instructions into a single string with a comma delimiter
                    row['Instructions'] = ', '.join(instructions)
                    
                    # check the meta.innerInstructions.instructions array for an object that 
                    # has a 'parsed' field with a 'type' of 'transfer' and a 'info' object
                    # with a 'source' field that matches 'FXSwRYKBwozWfCW4ya6M86NQ6QwikWPFZZhTqXnkV5es'
                    # and then convert the info.amount to a number, divide it by 100000000, then make it a 
                    # column in this row called 'Amount'
                    # for obj in event['meta'].get('innerInstructions', []):
                    #     for instruction in obj.get('instructions', []):
                    #         if instruction.get('parsed', {}).get('type') == 'transfer':
                    #             if instruction.get('parsed', {}).get('info', {}).get('source') == 'FXSwRYKBwozWfCW4ya6M86NQ6QwikWPFZZhTqXnkV5es':
                    #                 row['Amount'] = int(instruction.get('parsed', {}).get('info', {}).get('amount')) / 1000000000

                    # Find required object in 'postTokenBalances' with different 'owner' and get 'owner'
                    for obj in event['meta'].get('postTokenBalances', []):
                        if 'stake' in row['Instructions'].lower():
                            if obj.get('mint') == mint_address:
                                row['Owner'] = obj.get('owner')
                        else:
                            if (obj.get('mint') == 'GDfnEsia2WLAW5t8yx2X5j2mkfA74i5kwGdDuZHt7XmG' and 
                                obj.get('owner') != 'amaSM8gNkoeMBxRnREZ3hefA4FuEXSatcPsSD5nFx9X'):
                                row['Owner'] = obj.get('owner')

                    # Add Mint Address to the row
                    row['Mint Address'] = mint_address

                    row['Signature'] = signature

                    if 'StakePnft' in row['Instructions'] or 'StakeEdition' in row['Instructions']:
                        row['Type'] = 'Stake'

                    if 'UnstakePnft' in row['Instructions'] or 'UnstakeEdition' in row['Instructions']:
                        row['Type'] = 'Unstake'

                    # Before appending the row to csv_rows, check for duplicate signature
                    if row['Signature'] not in seen_signatures:
                        seen_signatures.add(row['Signature'])
                        if 'stake' in row['Instructions'].lower():
                            csv_rows.append(row)

    # Create DataFrame from the list of rows
    df = pd.DataFrame(csv_rows)

    return df



# Process the wallet directory
df = process_directory('../raw-pfp-transactions')

# Load the allocation data from the provided CSV
allocation_df = pd.read_csv('pfp-crown-allocation-dictionary.csv')

# Merge the two DataFrames based on the Mint address
merged_df = pd.merge(df, allocation_df, how='left', left_on='Mint Address', right_on='Mint')

# Drop the duplicate Mint column resulting from the merge
merged_df.drop('Mint', axis=1, inplace=True)

# Calculate the CROWN Per Minute
merged_df['CROWN Per Minute'] = merged_df['CrownAllocation'] / 1051200

# Save the merged data to a new CSV file
merged_df.to_csv('all-pfp-transactions.simplified.csv', index=False)
