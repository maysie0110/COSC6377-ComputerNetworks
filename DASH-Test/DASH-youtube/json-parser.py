import json
import csv

filename = 'logger'
def get_json_list():
    with open(filename+'.json') as file:
        data = json.load(file)
        return data
    
def write_to_csv(data):
    fieldnames = data[0].keys()
    
    with open(filename+'2.csv', 'w', encoding='utf8', newline='') as output_file:
        fc = csv.DictWriter(output_file, fieldnames= fieldnames)
        fc.writeheader()
        fc.writerows(data)
    
if __name__ == '__main__':
    data = get_json_list()
    write_to_csv(data)