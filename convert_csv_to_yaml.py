import csv
import yaml


def csv_to_yaml(csv_file, yaml_file):
    data = {}
    with open(csv_file, 'r') as f:
        csv_data = csv.reader(f)
        column_names = next(csv_data)
        for i, row in enumerate(csv_data):
            if any(field.strip() for field in row):
                data[f'user{i+1}'] = dict(zip(column_names, row))

    with open(yaml_file, 'w') as f:
        yaml.dump(data, f)

csv_to_yaml('users.csv', 'users.yaml')