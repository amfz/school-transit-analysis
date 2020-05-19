import json
import pandas
import polyline

trip_path = 'inputs/elpaso/pm_journeys.json'
elp_out = 'outputs/elpaso/pm_journeys_redo.geojson'

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


def extract_geocoded_data(result):
   """
   placeholder to extract lat/lon for student addresses, 
   eliminating the need for geocoding beforehand
   """ 
   pass


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
    Get itinerary attributes (origin, destination, start and end time, 
    trip duration) from a Google Directions API result leg.

    Walking-only routes do not have departure and arrival times -- those
    routes will have 'None' for those attributes.

    Args:
        trip (dict): a single Google Directions API response.

    Returns:
        dict: a dictionary of itinerary attributes.
    """
    start_address = leg['start_address']
    end_address = leg['end_address']
    # account for walking-only routes not having departure and arrival times
    dep_time = leg.get('departure_time', {}).get('text')
    arr_time = leg.get('arrival_time', {}).get('text')
    duration_minutes = round(leg['duration']['value'] / 60, 1)
    dist_miles = round(leg['distance']['value'] * 0.00062137, 2)
    attributes = {'origin': start_address,
                  'dest': end_address,
                  'departure_time': dep_time,
                  'arrival_time': arr_time,
                  'total_minutes': duration_minutes,
                  'total_miles': dist_miles,
                  'notes': []}
    return attributes


def extract_aggregate_step_attributes(steps):
    """
    Args:
        steps (list): the list of steps in a Google Directions API leg.
                      e.g. in `result['routes'][0]['legs'][0]['steps']`
    """
    
    total_walking_time = 0
    total_walking_dist = 0

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
            line = transit_details['line']['short_name']
            total_transit_time += step['duration']['value']
            transit_routes.append(line)
        elif step['travel_mode'] == 'WALKING':
            total_walking_time += step['duration']['value']
            total_walking_dist += step['duration']['value']
    
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
                      'routes_taken': transit_routes
                     }
    return agg_attributes


def make_feature(result):
    """
    Convert a Google Directions API result into a geojson feature, 
    with geometry and attributes.

    Args:
        result (dict): a single Google Directions API response.
    
    Returns:
        dict: A geojson-formatted feature.
    """
    obj = {'type': 'Feature'}
    if len(result['routes']) > 0:
        leg = result['routes'][0]['legs'][0]
        details = extract_leg_attributes(leg)
        agg_details = extract_aggregate_step_attributes(leg['steps'])
        details.update(agg_details)
        obj['properties'] = details
        geom = extract_overview_line(result)
        obj['geometry'] = {'type': 'LineString',
                           'coordinates': geom}
    else:
        waypts = result['geocoded_waypoints']      
        obj['properties'] = {'notes': result['status'],
                             'origin': waypts[0].get('address'),
                             'dest': waypts[1].get('address')}
        obj['geometry'] = {'type': 'GeometryCollection',
                           'coordinates': []}
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
        "crs": {
            "type": "name",
            "properties": {
                "name": "urn:ogc:def:crs:OGC:1.3:CRS84"
            }
        },
        "features": []
    }
    for journey in data:
        feature = make_feature(journey)
        out_geojson['features'].append(feature)

    return out_geojson


def write_geojson(geojson, out_path):
    """
    Write the geojson dict to file.
    """
    with open(out_path, 'w') as outfile:
        json.dump(geojson, outfile)    
    print('Wrote to {}'.format(out_path))
    return


def convert_to_geojson(json_file, out_path):
    """
    Load a JSON of Google Directions API results,
    convert it to a geojson, and write it to file.
    """
    data = load_data(json_file)
    print(len(data))
    geoj = gen_geojson(data)
    write_geojson(geoj, out_path)
    return geoj


convert_to_geojson(trip_path, elp_out)
