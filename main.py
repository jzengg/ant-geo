import csv
import io

import requests
import time

SPECIES_MASTER_LIST = 'species_master_list.csv'

REQUEST_DELAY_SECONDS = 5
BASE_URL = 'https://antmaps.org/api/v01'
# regions on the map where species is associated with (native, exotic, etc).
SPECIES_RANGE_URL = f'{BASE_URL}/species-range.json'
# dots on the map with specific locations for species
SPECIES_POINTS_URL = f'{BASE_URL}/species-points.json'
# directory of all regions mapping from the key to the actual name of the region
BENTITIES_URL = f'{BASE_URL}/bentities.json'
ALL_SPECIES = ['Acanthomyrmex.glabfemoralis', 'Camponotus.turkestanus', 'Myrmecocystus.mexicanus']


def get_species_points_records(species):
    print(f'getting points record for species {species}')
    payload = {'species': species}
    r = requests.get(SPECIES_POINTS_URL, params=payload)
    time.sleep(REQUEST_DELAY_SECONDS)
    return r.json()['records']


def get_species_region_records(species):
    print(f'getting region record for species {species}')
    payload = {'species': species}
    r = requests.get(SPECIES_RANGE_URL, params=payload)
    time.sleep(REQUEST_DELAY_SECONDS)
    return r.json()['bentities']


def get_all_regions():
    print('getting all regions')
    r = requests.get(BENTITIES_URL)
    data = r.json()['bentities']
    bentity_id_to_name = {bentity['key']: bentity['display'] for bentity in data}
    time.sleep(REQUEST_DELAY_SECONDS)
    return bentity_id_to_name


def write_json_to_csv(data, name):
    output = io.StringIO()
    writer = csv.writer(output)
    for index, row in enumerate(data):
        if index == 0:
            # Writing headers of CSV file
            header = row.keys()
            writer.writerow(header)
        # Writing data of CSV file
        writer.writerow(row.values())
    string = output.getvalue()
    with open(f'{name}.csv', 'w') as f:
        f.write(string)


def get_all_species_list():
    # strip byte order mark from file
    # s = open(SPECIES_MASTER_LIST, mode='r', encoding='utf-8-sig').read()
    # open(SPECIES_MASTER_LIST, mode='w', encoding='utf-8').write(s)
    with open(SPECIES_MASTER_LIST, encoding='utf8') as f:
        lines = f.readlines()
    cleaned = [l.strip() for l in lines]
    filtered = [l for l in cleaned if l]
    return filtered


if __name__ == '__main__':
    all_species_list = get_all_species_list()
    region_id_to_name = get_all_regions()
    all_species = []
    all_regions = []
    for species in all_species_list:
        point_records = get_species_points_records(species)
        for record in point_records:
            all_species.append(record)

        region_records = get_species_region_records(species)
        for record in region_records:
            region_id = record['gid']
            region_name = region_id_to_name[region_id]
            record_with_name = {**record, 'bentity_name': region_name, 'species_name': species}
            all_regions.append(record_with_name)
    write_json_to_csv(all_species, 'all_species')
    write_json_to_csv(all_regions, 'all_regions')



