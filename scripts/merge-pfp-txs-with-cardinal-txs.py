import pandas as pd
import json 
from datetime import datetime

# Assuming your dates are in the format YYYY-MM-DD or similar. Adjust accordingly if not.
DATE_FORMAT = "%m-%d-%Y"
JULY_25 = datetime.strptime("07-25-2023", DATE_FORMAT) 

def generate_owner_centric_json_with_crown_received(file_path, rewards_file_path):
    # Read CSV data
    df = pd.read_csv(file_path)

    # Convert date strings to datetime objects
    df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y %I:%M%p')
    
    # Load the rewards data
    rewards_df = pd.read_csv(rewards_file_path)
    
    # Calculate total reward received for each owner
    owner_rewards = rewards_df.groupby('To').sum()['Amount'].to_dict()

    owner_data = []

    # Group by owner
    for owner, group_df in df.groupby('Owner'):
        owner_block = {
            "owner": owner,
            "pfps": []
        }
        
        crown_total_for_owner = 0  # initialize the total

        # Iterate over unique mints for this owner
        for mint, mint_group in group_df.groupby('Mint Address'):
            pfp_info = {"mint": mint}

            # Get the stake and unstake date
            stake_date = mint_group[mint_group['Type'] == 'Stake']['Date'].min()

            # Switch unstake to today if it's after July 25, 2023 (basically they unstaked recently)
            unstake_date = mint_group[mint_group['Type'] == 'Unstake']['Date'].max()
                
            if unstake_date.to_pydatetime() > JULY_25:
                unstake_date = datetime.now()

            # Ensure both stake_date and unstake_date are valid
            if pd.notnull(stake_date) and pd.notnull(unstake_date):
                # Calculate total minutes staked
                delta = unstake_date - stake_date
                total_minutes_staked = delta.total_seconds() / 60

                # Calculate total crown due
                crown_per_minute = mint_group['CROWN Per Minute'].iloc[0]
                total_crown_due = total_minutes_staked * crown_per_minute

                # Update total crown for the owner
                crown_total_for_owner += total_crown_due

                # Update pfp_info dictionary
                pfp_info.update({
                    "staked": stake_date.strftime('%m/%d/%Y %I:%M%p'),
                    "unstaked": unstake_date.strftime('%m/%d/%Y %I:%M%p'),
                    "totalMinutesStaked": int(total_minutes_staked),
                    "totalCrownDue": total_crown_due
                })
                owner_block["pfps"].append(pfp_info)
                
        owner_block['crownDue'] = crown_total_for_owner  # add the total to the owner block
        
        # Add the crownReceived from the rewards data
        owner_block['crownReceived'] = owner_rewards.get(owner, 0.0)
        
        owner_data.append(owner_block)

    # Convert the list to JSON format
    with open('../preview-website/output_with_rewards.json', 'w') as json_file:
        json_file.write(json.dumps(owner_data, indent=4))

# call
generate_owner_centric_json_with_crown_received('all-pfp-transactions-simplified.csv', 'summed-cardinal-crown-rewards.csv')
