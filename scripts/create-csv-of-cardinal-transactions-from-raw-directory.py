import json
import datetime
import pandas as pd
import os

def process_directory(directory_path):
    csv_rows = []

    # Iterate over all the JSON files in the directory
    for filename in os.listdir(directory_path):
        if filename.endswith(".json"):
            file_path = os.path.join(directory_path, filename)

            # Open and load the JSON file
            with open(file_path) as file:
                data_list = json.load(file)

            # If data is indeed a list, then iterate over each event in the list
            for data in data_list:
                
                for event in [data]:  # Modified this line to wrap data in a list

                    if not isinstance(event['meta'], dict):
                        print(f"Expected dictionary, but got {type(event['meta'])} with value: {event['meta']}")
                        continue

                    # Get the date from blockTime
                    date = datetime.datetime.utcfromtimestamp(data['blockTime']).strftime('%-m/%-d/%Y %-I:%M%p')
                    post_balances = [x for x in event['meta'].get('postTokenBalances', []) if x['mint'] == 'GDfnEsia2WLAW5t8yx2X5j2mkfA74i5kwGdDuZHt7XmG' and x['owner'] != 'amaSM8gNkoeMBxRnREZ3hefA4FuEXSatcPsSD5nFx9X']
                    pre_balances = [x for x in event['meta'].get('preTokenBalances', []) if x['mint'] == 'GDfnEsia2WLAW5t8yx2X5j2mkfA74i5kwGdDuZHt7XmG' and x['owner'] != 'amaSM8gNkoeMBxRnREZ3hefA4FuEXSatcPsSD5nFx9X']
                    
                    if post_balances and pre_balances:
                        post_balance = post_balances[0]
                        pre_balance = pre_balances[0]

                        post_amount = post_balance['uiTokenAmount'].get('uiAmount', 0.0)
                        pre_amount = pre_balance['uiTokenAmount'].get('uiAmount', 0.0)

                        if post_amount is None:
                            post_amount = 0.0
                        if pre_amount is None:
                            pre_amount = 0.0

                        amount = post_amount - pre_amount
                        to_address = post_balance['owner']
                        
                        csv_rows.append({
                            'Date': date,
                            'Amount': amount,
                            'To': to_address
                        })

    return pd.DataFrame(csv_rows)

# Process the directory
df = process_directory('../raw-cardinal-transactions/')

# Save to CSV
df.to_csv('summed-cardinal-crown-rewards.csv', index=False)
