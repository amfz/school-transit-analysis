import json
import pandas as pd
import polyline

# school/time variables -- change before running
school = ''  # see schools list in main()
ampm = 'pm'

#path templates -- commented out because these are now generated in main()
#trip_path = 'temp/indy/{}_{}_journeys.json'.format(school, ampm)
#geojson_out_path = 'outputs/indy/{}_{}_journeys.geojson'.format(school, ampm)
#json_out_path = 'outputs/indy/{}_{}_journey_attributes.json'.format(school, ampm)
#csv_out_path = 'outputs/indy/{}_{}_journey_attributes.csv'.format(school, ampm)


def load_data(file_path):
    """
    Load a JSON as a dict from a file path.

    Args:
        file_path (str): path to JSON file.
    
    Returns:
        dict: dictionary of JSON data
    """
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data


def extract_overview_line(result):
    """
    Extract the overview polyline as a geojson-encoded list of points.

    Args:
        result (dict): a full Google Directions API response.

    Returns:
        list:  a list of (lon,lat) pairs corresponding to geom line vertices.
    """
    route_line = result['routes'][0]['overview_polyline']['points']
    pts = polyline.decode(route_line, geojson=True)
    return pts


def extract_leg_attributes(leg):
    """
    Get basic itinerary attributes (origin, destination, start and end time, 
    trip duration) from a Google Directions API result leg.

    Walking-only routes do not have departure and arrival times -- those
    routes will have 'None' for those attributes.

    Args:
        trip (dict): a single Google Directions API response.

    Returns:
        dict: a dictionary of itinerary attributes.
    """
    start_address = leg['start_address']
    start_lat = leg['start_location']['lat']
    start_lon = leg['start_location']['lng']
    end_address = leg['end_address']
    end_lat = leg['end_location']['lat']
    end_lon = leg['end_location']['lng']
    # account for walking-only routes not having departure and arrival times
    dep_time = leg.get('departure_time', {}).get('text')
    arr_time = leg.get('arrival_time', {}).get('text')
    duration_minutes = round(leg['duration']['value'] / 60, 1)
    dist_miles = round(leg['distance']['value'] * 0.00062137, 2)
    attributes = {'origin': start_address,
                  'origin_lat': start_lat,
                  'origin_lon': start_lon,
                  'dest': end_address,
                  'dest_lat': end_lat,
                  'dest_lon': end_lon,
                  'departure_time': dep_time,
                  'arrival_time': arr_time,
                  'total_minutes': duration_minutes,
                  'total_miles': dist_miles,
                  'notes': ''}
    return attributes


def extract_aggregate_step_attributes(steps):
    """
    Get further itinerary attributes (walk time, transit time, 
    number of transfers, specific routes taken) from a Google Directions API result leg.

    Args:
        steps (list): the list of steps in a Google Directions API leg.
                      e.g. in `result['routes'][0]['legs'][0]['steps']`

    Returns:
        dict: dictionary of itinerary attributes
    """
    
    total_walking_time = 0
    total_walking_dist = 0
    #transit-specific attributes
    total_transit_time = 0
    transit_routes = []
    starting_stop = None
    end_stop = None

    for step in steps:
        if step['travel_mode'] == 'TRANSIT':
            transit_details = step['transit_details']
            if starting_stop is None:
                starting_stop = transit_details['departure_stop']['name']
            end_stop = transit_details['arrival_stop']['name']
            line = transit_details.get('line', {}).get('short_name', transit_details['line']['name'])
            total_transit_time += step['duration']['value']
            transit_routes.append(line)
        elif step['travel_mode'] == 'WALKING':
            total_walking_time += step['duration']['value']
            total_walking_dist += step['distance']['value']
    
    # calculate the number of transfers
    if len(transit_routes) > 0:
        num_transfers = len(transit_routes) - 1
    else:
        num_transfers = 0

    agg_attributes = {'walk_time_minutes': round(total_walking_time / 60, 1),
                      'walk_dist_miles': round(total_walking_dist * 0.00062137, 2),
                      'transit_time_minutes': round(total_transit_time / 60, 1),
                      'num_transfers': num_transfers,
                      'starting_stop': starting_stop,
                      'end_stop': end_stop,
                      'routes_taken': ', '.join(transit_routes)
                     }
    return agg_attributes


def extract_properties(result):
    if len(result['routes']) > 0:
        leg = result['routes'][0]['legs'][0]
        properties = extract_leg_attributes(leg)
        agg_details = extract_aggregate_step_attributes(leg['steps'])
        properties.update(agg_details)
    else:
        waypts = result['geocoded_waypoints']      
        properties = {'notes': result['status'],
                      'origin': waypts[0].get('address'),
                      'dest': waypts[1].get('address')}
    return properties


def make_feature(result):
    """
    Convert a Google Directions API result into a geojson feature, 
    with geometry and attributes.

    Args:
        result (dict): a single Google Directions API response.
    
    Returns:
        dict: A single geojson-formatted feature.
    """
    obj = {'type': 'Feature'}
    if len(result['routes']) > 0:
        geom = extract_overview_line(result)
        obj['geometry'] = {'type': 'LineString',
                           'coordinates': geom}
    else:
        obj['geometry'] = {'type': 'GeometryCollection',
                           'coordinates': []}
    obj['properties'] = extract_properties(result)
    return obj


def gen_geojson(data):
    """
    Create a fully-formed geojson from Google Directions API results.
    Note that features will not be created for trips the API could not route.

    Args:
        data (dict): A loaded JSON of Google Directions API results.
    
    Returns:
        dict: A geojson-compliant dictionary of trip features.
    """
    out_geojson = {
        "type": "FeatureCollection",
        "name": "trips",
        "features": []
    }
    for journey in data:
        feature = make_feature(journey)
        out_geojson['features'].append(feature)

    return out_geojson


def write_geojson(geojson, out_path):
    """
    Write the geojson dict to file.

    Args:
        geojson (dict): The geoJSON-formatted dictionary to write to file.
    """
    with open(out_path, 'w') as outfile:
        json.dump(geojson, outfile)    
    print('Wrote to {}'.format(out_path))


def convert_to_geojson(result_file, geo_out_path):
    """
    Load a JSON of Google Directions API results,
    convert it to a geojson, and write it to file.
    """
    data = load_data(result_file)
    print(len(data))
    geoj = gen_geojson(data)

    # add any notes
    for f in geoj['features']:
        dep_time = f.get('properties', {}).get('departure_time', '')
        if 'am' in geo_out_path and 'pm' in str(dep_time):
            f['properties']['notes'] += 'PM Departure'
    write_geojson(geoj, geo_out_path)


def gen_json(result_file, out_path='', write_file=False):
    """
    Given a json file of Directions API results, 
    produce a json dataset for analysis, and write it to file.
    """
    data = load_data(result_file)
    records = []
    for journey in data:
        record = extract_properties(journey)
        dep_time = record.get('departure_time', '')
        if '_am_' in out_path and 'pm' in str(dep_time):
            record['notes'] += 'PM Departure'
        records.append(record)
    
    if write_file:
        with open(out_path, 'w') as outfile:
            json.dump(records, outfile)
            print('Wrote to {}'.format(out_path))

    return records


def convert_json_to_csv(json_path):
    csv_path = json_path[:-5] + '.csv'
    print(csv_path)
    data = pd.read_json(json_path)
    data.to_csv(csv_path, index=False)


def main():
    schools = ['000_example_school',
               '999_school_two'
              ]
    
    for school in schools:
        trip_path = 'temp/indy/{}_{}_journeys.json'.format(school, ampm)

        # uncomment to get geojson files
        #geojson_out_path = 'outputs/indy/{}_{}_journeys.geojson'.format(school, ampm)
        #convert_to_geojson(trip_path, geojson_out_path)

        csv_out_path = 'outputs/indy/{}_{}_journey_attributes.csv'.format(school, ampm)
        j = gen_json(trip_path, write_file=False)
        jdf = pd.DataFrame.from_dict(j)
        jdf.to_csv(csv_out_path, index=False)
        print('Wrote to {}'.format(csv_out_path))


if __name__ == '__main__':
    main()
