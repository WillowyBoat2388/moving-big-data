import pandas as pd

# Local file directories
# These paths can be updated to meet your testing environment needs.
# source_path = "../data/Stocks/"
# save_path = "../data/Output/"
# index_file_path = '../data/top_companies.txt'

# # EC2 file directories
# Do not change these paths
source_path = "/home/ec2-user/s3-drive/Stocks/"
save_path = "/home/ec2-user/s3-drive/Output/"
index_file_path = "/home/ec2-user/s3-drive/CompanyNames/top_companies.txt"

def extract_companies_from_index(index_file_path):
    """Generate a list of company files that need to be processed. 

    Args:
        index_file_path (str): path to index file

    Returns:
        list: Names of company names. 
    """
    company_file = open(index_file_path, "r")
    contents = company_file.read()
    contents = contents.replace("'","")
    contents_list = contents.split(",")
    cleaned_contents_list = [item.strip() for item in contents_list]
    company_file.close()
    return cleaned_contents_list

def get_path_to_company_data(list_of_companies, source_data_path):
    """Creates a list of the paths to the company data
       that will be processed

    Args:
        list_of_companies (list): Extracted `.csv` file names of companies whose data needs to be processed.
        source_data_path (str): Path to where the company `.csv` files are stored. 

    Returns:
        [type]: [description]
    """
    path_to_company_data = []
    for file_name in list_of_companies:
        path_to_company_data.append(source_data_path + file_name)
    return path_to_company_data

def save_table(dataframe, output_path, file_name, header):
    """Saves an input pandas dataframe as a CSV file according to input parameters.

    Args:
        dataframe (pandas.dataframe): Input dataframe.
        output_path (str): Path to which the resulting `.csv` file should be saved. 
        file_name (str): The name of the output `.csv` file. 
        header (boolean): Whether to include column headings in the output file.
    """
    print(f"Path = {output_path}, file = {file_name}")
    dataframe.to_csv(output_path + file_name + ".csv", index=False, header=header)


def data_processing(file_paths, output_path):
    """Process and collate company csv file data for use within the data processing component of the formed data pipeline.  

    Args:
        file_paths (list[str]): A list of paths to the company csv files that need to be processed. 
        output_path (str): The path to save the resulting csv file to.  
    """

    # INSERT YOUR CODE HERE
    out_df = []
    for path in file_paths:
        company = open(path, "r")
        content = company.read(1)
        if content:
            df = pd.read_csv(company)
            df.drop('OpenInt', inplace=True, axis=1)
            df['daily_percent_change'] = ((df['Close'] - df['Open'])/df['Open']) * 100
            df['value_change'] = df['Close'] - df['Open']
            df['company_name']  = path[len(output_path):-4]
            df.rename(columns = {'Date':'stock_date', 'Open':'open_value','High':'high_value','Low':'low_value', 'Close':'close_value', 'Volume':'volume_traded'}, inplace = True)
            out_df.append(df)
        else:
            continue
    df = pd.concat(out_df)
    file_name = "historical_stock_data"

    save_table(df, output_path, file_name, False)

if __name__ == "__main__":

    # Get all file names in source data directory of companies whose data needs to be processed, 
    # This information is specified within the `top_companies.txt` file. 
    file_names = extract_companies_from_index(index_file_path)

    # Update the company file names to include path information. 
    path_to_company_data = get_path_to_company_data(file_names, source_path)

    # Process company data and create full data output
    data_processing(path_to_company_data, save_path)