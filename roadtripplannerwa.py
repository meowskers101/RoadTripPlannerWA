# NEED TO INSTALL STREAMLIT 
# USE A VIRTUAL ENVIRONMENT TO INSTALL AND RUN THE CODE
# NEED THE OTHER PYTHON FILE (wa_counties.py) TO USE ITS DICTIONARIES
import streamlit as st
from collections import deque
from wa_counties import (wa_highway_connections, county_coords, wa_county_graph, 
                         get_drive_time, city_coords, city_to_county, 
                         get_cities_by_county, get_city_drive_time)
import math
import requests

import shelve
import time
import matplotlib
# Use a non-interactive backend suitable for headless servers (Streamlit hosting)
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import json
import os

# Try to import interactive map libraries; if unavailable we'll fall back to matplotlib
try:
    import pandas as pd
    import pydeck as pdk
    _HAS_PYDECK = True
except Exception:
    _HAS_PYDECK = False

# Try to import shapely and geopandas for county borders
try:
    import geopandas as gpd
    from shapely.geometry import Point, Polygon
    _HAS_GEOPANDAS = True
except Exception:
    _HAS_GEOPANDAS = False

# Use the graph from wa_counties module
wa_graph = wa_county_graph


def create_simple_county_borders():
    """Create simplified rectangular county borders as a fallback."""
    features = []
    
    # Create approximate rectangular boundaries for each county
    for county, (lat, lon) in county_coords.items():
        # Create a small box around each county center
        size = 0.3  # degrees
        features.append({
            "type": "Feature",
            "properties": {"name": county},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [lon - size, lat - size],
                    [lon + size, lat - size],
                    [lon + size, lat + size],
                    [lon - size, lat + size],
                    [lon - size, lat - size]
                ]]
            }
        })
    
    return {
        "type": "FeatureCollection",
        "features": features
    }


def download_county_borders():
    """Download Washington state county borders from online source."""
    
    urls = [
        "https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json",
        "https://raw.githubusercontent.com/deldersveld/topojson/master/countries/us-states/WA-53-washington-counties.json"
    ]
    
    for url in urls:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                # Filter for Washington state if needed
                if 'features' in data:
                    # Check if it's US-wide and filter for WA (FIPS code 53)
                    wa_features = [f for f in data['features'] 
                                 if f.get('properties', {}).get('STATE', '')[:2] == '53' or
                                    f.get('id', '')[:2] == '53']
                    if wa_features:
                        data['features'] = wa_features
                        return data
                return data
        except:
            continue
    
    # If all downloads fail, return simplified borders
    return create_simple_county_borders()


def load_county_borders():
    """Load Washington state county borders from a GeoJSON file or download if not available."""
    geojson_path = os.path.join(os.path.dirname(__file__), 'wa_counties.geojson')
    
    # Try to load existing file
    if os.path.exists(geojson_path):
        try:
            with open(geojson_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            st.warning(f"Failed to load existing county borders: {e}")
    
    # Try to download if file doesn't exist
    try:
        data = download_county_borders()
        if data:
            # Save for future use
            try:
                with open(geojson_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f)
            except:
                pass  # Continue even if we can't save
            return data
    except Exception as e:
        # Last resort: return simplified borders
        return create_simple_county_borders()
    
    return create_simple_county_borders()


def plot_map(graph, coords, route=None, show_edges=True, show_labels=True, geojson=None, route_cities=None):
    """Create a matplotlib figure plotting counties and adjacency lines.
    route: ordered list of county names to highlight as the route (drawn in red).
    route_cities: dictionary mapping counties to their selected cities.
    """
    fig, ax = plt.subplots(figsize=(14, 10))

    # Draw county borders from GeoJSON if available
    if geojson and _HAS_GEOPANDAS:
        try:
            gdf = gpd.GeoDataFrame.from_features(geojson['features'])
            gdf.plot(ax=ax, facecolor='lightgray', edgecolor='black', linewidth=0.8, alpha=0.3, zorder=0)
        except Exception as e:
            st.warning(f"Could not plot county borders: {e}")
    elif geojson:
        # Fallback to matplotlib patches if geopandas not available
        try:
            from matplotlib.patches import Polygon as MplPolygon
            for feature in geojson.get("features", []):
                geom = feature.get("geometry", {})
                props = feature.get("properties", {})
                coords_list = []
                if geom.get("type") == "Polygon":
                    coords_list = [geom.get("coordinates", [])]
                elif geom.get("type") == "MultiPolygon":
                    coords_list = geom.get("coordinates", [])

                for poly in coords_list:
                    if not poly:
                        continue
                    exterior = poly[0]
                    xy = [(pt[0], pt[1]) for pt in exterior]
                    patch = MplPolygon(xy, closed=True, facecolor='lightgray', 
                                     edgecolor='black', linewidth=0.8, alpha=0.3, zorder=0)
                    ax.add_patch(patch)
        except Exception as e:
            st.warning(f"Could not plot county borders with matplotlib: {e}")

    # Draw adjacency edges (light blue)
    edges_drawn = set()
    for county, neighbors in graph.items():
        if county not in coords:
            continue
        for neighbor in neighbors:
            if neighbor not in coords:
                continue
            key = tuple(sorted((county, neighbor)))
            if key in edges_drawn:
                continue
            edges_drawn.add(key)
            if show_edges:
                lat1, lon1 = coords[county]
                lat2, lon2 = coords[neighbor]
                ax.plot([lon1, lon2], [lat1, lat2], color='lightblue', linewidth=1.2, 
                       alpha=0.6, zorder=1)

    # Draw county center points
    xs = []
    ys = []
    labels = []
    for county, (lat, lon) in coords.items():
        xs.append(lon)
        ys.append(lat)
        labels.append(county)

    ax.scatter(xs, ys, s=60, c='navy', zorder=2, edgecolors='white', linewidths=1)

    # County labels
    if show_labels:
        for label, x, y in zip(labels, xs, ys):
            ax.text(x, y, label, fontsize=8, zorder=3, ha='center', va='center',
                   weight='bold',
                   bbox=dict(boxstyle='round,pad=0.4', facecolor='white', 
                            edgecolor='gray', alpha=0.85, linewidth=0.5))

    # If a route is provided, draw it with arrows showing direction
    if route and route_cities:
        from matplotlib.patches import FancyArrowPatch
        
        # Build list of city coordinates for the route
        route_city_coords = []
        for county in route:
            if county in route_cities and route_cities[county]:
                city = route_cities[county]
                if city in city_coords:
                    lat, lon = city_coords[city]
                    route_city_coords.append((lat, lon, city, county))
                elif county in coords:
                    lat, lon = coords[county]
                    route_city_coords.append((lat, lon, None, county))
            elif county in coords:
                lat, lon = coords[county]
                route_city_coords.append((lat, lon, None, county))
        
        # Track which edges we've drawn to curve bidirectional ones
        route_edges = {}
        for i in range(len(route_city_coords) - 1):
            edge = (i, i+1)
            reverse_edge = (i+1, i)
            
            if reverse_edge in route_edges:
                route_edges[edge] = 'curve'
                route_edges[reverse_edge] = 'curve'
            else:
                route_edges[edge] = 'straight'
        
        # Draw route segments with arrows
        for i in range(len(route_city_coords) - 1):
            lat1, lon1, city1, county1 = route_city_coords[i]
            lat2, lon2, city2, county2 = route_city_coords[i+1]
            
            edge = (i, i+1)
            
            # If this edge needs to curve (bidirectional)
            if route_edges.get(edge) == 'curve':
                dx = lon2 - lon1
                dy = lat2 - lat1
                length = math.sqrt(dx**2 + dy**2)
                if length > 0:
                    perp_x = -dy / length * 0.15
                    perp_y = dx / length * 0.15
                    
                    arrow = FancyArrowPatch(
                        (lon1, lat1), (lon2, lat2),
                        connectionstyle=f"arc3,rad=0.3",
                        arrowstyle='->,head_width=0.4,head_length=0.8',
                        color='red',
                        linewidth=3,
                        alpha=0.8,
                        zorder=4
                    )
                    ax.add_patch(arrow)
            else:
                arrow = FancyArrowPatch(
                    (lon1, lat1), (lon2, lat2),
                    arrowstyle='->,head_width=0.4,head_length=0.8',
                    color='red',
                    linewidth=3,
                    alpha=0.8,
                    zorder=4
                )
                ax.add_patch(arrow)
        
        # Draw city markers on the route
        if len(route_city_coords) >= 1:
            lats = [c[0] for c in route_city_coords]
            lons = [c[1] for c in route_city_coords]
            ax.scatter(lons, lats, s=120, c='red', zorder=5, edgecolors='darkred', linewidths=2, marker='D')
            
            # Add city labels and route step numbers
            for i, (lat, lon, city, county) in enumerate(route_city_coords):
                # Step number
                ax.text(lon, lat, str(i+1), fontsize=9, zorder=6, ha='center', va='center',
                       color='white', weight='bold')
                
                # City name if available
                if city:
                    ax.text(lon, lat - 0.12, city, fontsize=7, zorder=6, ha='center', va='top',
                           style='italic', color='darkred', weight='bold',
                           bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8))

    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.set_title('Washington State Counties and Highway Connections', fontsize=14, weight='bold')
    ax.set_aspect('equal', adjustable='datalim')
    ax.grid(True, linestyle=':', linewidth=0.5, alpha=0.5)
    
    # Add legend
    if route:
        from matplotlib.lines import Line2D
        from matplotlib.patches import FancyArrowPatch
        legend_elements = [
            Line2D([0], [0], color='lightblue', lw=2, label='County Connections'),
            FancyArrowPatch((0, 0), (0.1, 0.1), arrowstyle='->', color='red', lw=3, label='Your Route'),
            Line2D([0], [0], marker='D', color='w', markerfacecolor='red', 
                   markersize=10, label='Route Cities', linestyle='None')
        ]
        ax.legend(handles=legend_elements, loc='upper right')
    
    return fig


def show_interactive_map(graph, coords, route=None, show_edges=True, show_labels=True, geojson=None, route_cities=None):
    """Use pydeck to show an interactive map with points, adjacency lines, and an optional route."""
    if not _HAS_PYDECK:
        return None

    layers = []

    # Add county borders from GeoJSON
    if geojson:
        try:
            geo_layer = pdk.Layer(
                "GeoJsonLayer",
                data=geojson,
                stroked=True,
                filled=True,
                get_fill_color=[200, 200, 200, 50],
                get_line_color=[80, 80, 80],
                line_width_min_pixels=2,
                pickable=True,
            )
            layers.append(geo_layer)
            
            # Add county name labels at centroids
            if geojson.get('features'):
                label_data = []
                for feature in geojson['features']:
                    props = feature.get('properties', {})
                    county_name = props.get('name', props.get('NAME', ''))
                    
                    # Get centroid from our coords if available
                    if county_name in coords:
                        lat, lon = coords[county_name]
                        label_data.append({
                            "name": county_name,
                            "lat": lat,
                            "lon": lon
                        })
                
                if label_data:
                    labels_df = pd.DataFrame(label_data)
                    county_labels = pdk.Layer(
                        "TextLayer",
                        data=labels_df,
                        get_position='[lon, lat]',
                        get_text='name',
                        get_size=13,
                        get_color=[40, 40, 40, 200],
                        get_alignment_baseline='center',
                        get_background_color=[255, 255, 255, 180],
                        background_padding=[4, 2, 4, 2],
                        font_family='Arial, sans-serif',
                        font_weight='bold',
                        pickable=False,
                    )
                    layers.append(county_labels)
        except Exception as e:
            st.warning(f"Could not add GeoJSON layer: {e}")

    # Prepare county points dataframe
    rows = []
    for name, (lat, lon) in coords.items():
        rows.append({"name": name, "lat": lat, "lon": lon})
    points = pd.DataFrame(rows)

    # Edges
    edges = []
    edges_seen = set()
    for county, neighbors in graph.items():
        if county not in coords:
            continue
        for neighbor in neighbors:
            if neighbor not in coords:
                continue
            key = tuple(sorted((county, neighbor)))
            if key in edges_seen:
                continue
            edges_seen.add(key)
            lat1, lon1 = coords[county]
            lat2, lon2 = coords[neighbor]
            edges.append({"start": [lon1, lat1], "end": [lon2, lat2]})

    # Line layer for adjacencies
    if show_edges and edges:
        line_layer = pdk.Layer(
            "LineLayer",
            data=edges,
            get_source_position="start",
            get_target_position="end",
            get_width=2,
            get_color=[100, 150, 200, 150],
            pickable=False,
        )
        layers.append(line_layer)

    # Scatter layer for county centers
    scatter = pdk.Layer(
        "ScatterplotLayer",
        data=points,
        get_position='[lon, lat]',
        get_fill_color=[10, 30, 160],
        get_radius=8000,
        pickable=True,
        auto_highlight=True,
    )
    layers.append(scatter)

    # Always show county labels (not optional anymore for better UX)
    text_layer = pdk.Layer(
        "TextLayer",
        data=points,
        get_position='[lon, lat]',
        get_text='name',
        get_size=14,
        get_color=[0, 0, 0],
        get_alignment_baseline='bottom',
        get_background_color=[255, 255, 255, 200],
        background_padding=[3, 2, 3, 2],
        font_weight='600',
        pickable=False,
    )
    layers.append(text_layer)

    # Route overlay with arrows and city markers
    if route and len(route) >= 2 and route_cities:
        # Build city coordinates for the route
        route_city_data = []
        for i, county in enumerate(route):
            if county in route_cities and route_cities[county]:
                city = route_cities[county]
                if city in city_coords:
                    lat, lon = city_coords[city]
                    route_city_data.append({
                        "lat": lat, "lon": lon, "city": city, 
                        "county": county, "step": i+1
                    })
                elif county in coords:
                    lat, lon = coords[county]
                    route_city_data.append({
                        "lat": lat, "lon": lon, "city": None, 
                        "county": county, "step": i+1
                    })
            elif county in coords:
                lat, lon = coords[county]
                route_city_data.append({
                    "lat": lat, "lon": lon, "city": None, 
                    "county": county, "step": i+1
                })
        
        # Build path segments
        path_segments = []
        for i in range(len(route_city_data) - 1):
            current = route_city_data[i]
            next_stop = route_city_data[i+1]
            
            path_segments.append({
                "path": [[current["lon"], current["lat"]], [next_stop["lon"], next_stop["lat"]]],
                "color": [240, 50, 50, 200]
            })
        
        if path_segments:
            path_layer = pdk.Layer(
                "PathLayer",
                data=path_segments,
                get_path="path",
                get_color="color",
                width_scale=20,
                width_min_pixels=4,
                get_width=1,
            )
            layers.append(path_layer)
        
        # Add city markers (diamond shaped)
        if route_city_data:
            cities_df = pd.DataFrame(route_city_data)
            
            # Route city markers
            city_scatter = pdk.Layer(
                "ScatterplotLayer",
                data=cities_df,
                get_position='[lon, lat]',
                get_fill_color=[240, 50, 50],
                get_radius=12000,
                pickable=True,
                auto_highlight=True,
            )
            layers.append(city_scatter)
            
            # Step numbers
            step_text = pdk.Layer(
                "TextLayer",
                data=cities_df,
                get_position='[lon, lat]',
                get_text='step',
                get_size=16,
                get_color=[255, 255, 255],
                get_alignment_baseline='center',
                font_weight='bold',
                pickable=False,
            )
            layers.append(step_text)
            
            # City name labels
            cities_with_names = cities_df[cities_df['city'].notna()]
            if len(cities_with_names) > 0:
                city_labels = pdk.Layer(
                    "TextLayer",
                    data=cities_with_names,
                    get_position='[lon, lat]',
                    get_text='city',
                    get_size=12,
                    get_color=[139, 0, 0],
                    get_alignment_baseline='top',
                    get_background_color=[255, 255, 255, 220],
                    background_padding=[2, 1, 2, 1],
                    font_weight='bold',
                    font_style='italic',
                    pickable=False,
                )
                layers.append(city_labels)

    # View centered on Washington State
    view_state = pdk.ViewState(latitude=47.3, longitude=-120.5, zoom=6.5)

    deck = pdk.Deck(layers=layers, initial_view_state=view_state, 
                   tooltip={"text": "{name}\n{city}\n{county}"})
    return deck


def bfs_path(graph, start, goal):
    """Find shortest path using BFS."""
    queue = deque([start])
    visited = set()
    parent = {}

    while queue:
        current = queue.popleft()
        visited.add(current)

        if current == goal:
            # reconstruct path
            path = [current]
            while current in parent:
                current = parent[current]
                path.append(current)
            path.reverse()
            return path

        for neighbor in graph[current]:
            if neighbor not in visited and neighbor not in queue:
                queue.append(neighbor)
                parent[neighbor] = current
    return None


def find_fastest_city_for_route(county, prev_county, next_county, prev_city, next_city, cities_by_county):
    """
    Find the fastest city to go through in a county based on the specific route.
    Takes into account the actual cities in adjacent counties for precise calculation.
    """
    if county not in cities_by_county:
        return None
    
    cities = cities_by_county[county]
    if not cities:
        return None
    
    # If only one city, return it
    if len(cities) == 1:
        return cities[0]
    
    best_city = None
    best_time = float('inf')
    
    # For each candidate city, calculate the actual detour/path time
    for city in cities:
        if city not in city_coords:
            continue
        
        city_lat, city_lon = city_coords[city]
        total_distance = 0
        
        # Calculate distance from previous city/county
        if prev_city and prev_city in city_coords:
            prev_lat, prev_lon = city_coords[prev_city]
            dist_from_prev = math.sqrt((city_lat - prev_lat)**2 + (city_lon - prev_lon)**2)
            total_distance += dist_from_prev
        elif prev_county and prev_county in county_coords:
            prev_lat, prev_lon = county_coords[prev_county]
            dist_from_prev = math.sqrt((city_lat - prev_lat)**2 + (city_lon - prev_lon)**2)
            total_distance += dist_from_prev
        
        # Calculate distance to next city/county
        if next_city and next_city in city_coords:
            next_lat, next_lon = city_coords[next_city]
            dist_to_next = math.sqrt((city_lat - next_lat)**2 + (city_lon - next_lon)**2)
            total_distance += dist_to_next
        elif next_county and next_county in county_coords:
            next_lat, next_lon = county_coords[next_county]
            dist_to_next = math.sqrt((city_lat - next_lat)**2 + (city_lon - next_lon)**2)
            total_distance += dist_to_next
        
        if total_distance < best_time:
            best_time = total_distance
            best_city = city
    
    return best_city if best_city else cities[0]


def calculate_route_with_fastest_cities(route, route_cities, cities_by_county):
    """
    For each county in the route, determine the fastest city to go through.
    Takes into account the specific cities selected for adjacent counties.
    Returns a dictionary mapping county -> fastest city for this route.
    """
    fastest_cities = {}
    
    for i, county in enumerate(route):
        # Get previous and next counties and their cities
        prev_county = route[i-1] if i > 0 else None
        next_county = route[i+1] if i < len(route) - 1 else None
        
        prev_city = route_cities.get(prev_county) if prev_county else None
        next_city = route_cities.get(next_county) if next_county else None
        
        # If this county already has a selected city, use it
        if county in route_cities and route_cities[county]:
            fastest_cities[county] = route_cities[county]
        else:
            # Calculate the fastest city for this position in the route
            fastest_city = find_fastest_city_for_route(
                county, prev_county, next_county, prev_city, next_city, cities_by_county
            )
            if fastest_city:
                fastest_cities[county] = fastest_city
    
    return fastest_cities
    

def find_optimal_route(graph, start, end, must_visit):
    """Find the most time-efficient route that visits all must-visit counties.
    Uses a greedy nearest-neighbor approach with all permutations for small sets.
    Returns a full path (list of counties) or None if no path found.
    """
    from itertools import permutations

    if not must_visit:
        return bfs_path(graph, start, end)

    # For small sets (≤7), try all permutations to find truly optimal route
    if len(must_visit) <= 7:
        best_route = None
        best_time = float('inf')

        for perm in permutations(must_visit):
            route_points = list(perm) + [end]
            prev = start
            full_path = []
            total_time = 0
            path_found = True

            for target in route_points:
                subpath = bfs_path(graph, prev, target)
                if subpath is None:
                    path_found = False
                    break

                for i in range(len(subpath) - 1):
                    total_time += get_drive_time(subpath[i], subpath[i + 1])

                if not full_path:
                    full_path.extend(subpath)
                else:
                    full_path.extend(subpath[1:])
                prev = target

            if path_found and total_time < best_time:
                best_time = total_time
                best_route = full_path

        return best_route

    # For larger sets, use greedy nearest-neighbor approach
    remaining = set(must_visit)
    current = start
    full_path = [start]

    while remaining:
        best_next = None
        best_subpath = None
        best_time = float('inf')

        for county in remaining:
            subpath = bfs_path(graph, current, county)
            if subpath:
                path_time = sum(get_drive_time(subpath[i], subpath[i + 1])
                                for i in range(len(subpath) - 1))
                if path_time < best_time:
                    best_time = path_time
                    best_next = county
                    best_subpath = subpath

        if best_next is None:
            return None

        full_path.extend(best_subpath[1:])
        current = best_next
        remaining.remove(best_next)

    final_path = bfs_path(graph, current, end)
    if final_path:
        full_path.extend(final_path[1:])
        return final_path if not full_path else full_path
    return None


def find_best_city_detour(graph, route, city_name):
    """
    Find the best place to insert a city visit into an existing route.
    Returns the modified route and the detour time in seconds.
    """
    if city_name not in city_to_county:
        return None, None, None
    
    target_county = city_to_county[city_name]
    
    # If county is already in route, no detour needed
    if target_county in route:
        detour_time = 0
        insertion_index = route.index(target_county)
        return route, detour_time, insertion_index
    
    # Try inserting the county at each position in the route
    best_route = None
    best_detour = float('inf')
    best_index = -1
    
    original_time = sum(get_drive_time(route[i], route[i+1]) 
                       for i in range(len(route)-1))
    
    for i in range(len(route)):
        # Try inserting target_county after position i
        if i == 0:
            # Insert at beginning
            new_segment = bfs_path(graph, route[0], target_county)
            if new_segment:
                test_route = new_segment + route[1:]
        elif i == len(route) - 1:
            # Insert at end
            new_segment = bfs_path(graph, route[-1], target_county)
            if new_segment:
                test_route = route + new_segment[1:]
        else:
            # Insert in middle
            path_to = bfs_path(graph, route[i], target_county)
            path_from = bfs_path(graph, target_county, route[i+1])
            
            if path_to and path_from:
                test_route = route[:i+1] + path_to[1:] + path_from[1:]
            else:
                continue
        
        # Calculate new total time
        new_time = sum(get_drive_time(test_route[j], test_route[j+1]) 
                      for j in range(len(test_route)-1))
        detour = new_time - original_time
        
        if detour < best_detour:
            best_detour = detour
            best_route = test_route
            best_index = i
    
    return best_route, best_detour, best_index


def get_route_highways(route, highway_data):
    """Extract the highways used between consecutive counties in the route."""
    highways_used = []
    for i in range(len(route) - 1):
        current = route[i]
        next_county = route[i + 1]
        
        # Get drive time between counties
        drive_time = get_drive_time(current, next_county)
        
        # Find highways that connect these counties
        if current in highway_data:
            found_highways = set()
            for city, highways in highway_data[current]['connections'].items():
                for highway, destinations in highways.items():
                    for dest in destinations:
                        if f"({next_county} Co.)" in dest or f"({next_county})" in dest:
                            found_highways.add(highway)
            
            if found_highways:
                highways_used.append({
                    'from': current,
                    'to': next_county,
                    'highways': sorted(list(found_highways)),
                    'time': drive_time
                })
            else:
                # No direct highway found in data, just note the connection
                highways_used.append({
                    'from': current,
                    'to': next_county,
                    'highways': ['Direct connection'],
                    'time': drive_time
                })
        else:
            highways_used.append({
                'from': current,
                'to': next_county,
                'highways': ['Route available'],
                'time': drive_time
            })
    
    return highways_used


# Streamlit App
st.set_page_config(page_title="WA County Road Trip", page_icon="🚗", layout="wide")

# Initialize session state
if 'button_clicked' not in st.session_state:
    st.session_state.button_clicked = False

st.title("Washington State County Road Trip Planner 🚗")
st.write("Plan your road trip across Washington State counties using major highways!")

# Try to load county borders
geojson = load_county_borders()

if geojson and geojson.get('features'):
    num_features = len(geojson['features'])
    st.success(f"✓ County borders loaded successfully! ({num_features} counties)")
else:
    st.warning("⚠️ Using simplified county borders")

col1, col2 = st.columns(2)

with col1:
    counties = sorted(list(wa_graph.keys()))
    cities_by_county = get_cities_by_county()
    
    # Build dropdown options organized by county with route-specific fastest
    def build_location_options(route_fastest=None):
        options = []
        for county in counties:
            # Add "Fastest route through [County]" option - dynamically calculated
            if route_fastest and county in route_fastest:
                fastest_city = route_fastest[county]
                options.append(f"Fastest for your route: {fastest_city} ({county})")
            else:
                # Placeholder - will be calculated after route is determined
                options.append(f"Fastest route through {county}")
            
            # Add individual cities in this county
            if county in cities_by_county:
                for city in cities_by_county[county]:
                    options.append(f"   {city} ({county})")
            
            # Add separator except for last county
            if county != counties[-1]:
                options.append("─" * 50)
        
        return options
    
    location_options = build_location_options()
    
    start_selection = st.selectbox("Start Location", location_options, key="start")
    end_selection = st.selectbox("End Location", location_options, key="end")
    
    # Parse selection
    def parse_selection(selection):
        if not selection or "─" in selection:
            return None, None, False
        s = selection.strip()

        # Check for explicit "Fastest for your route: City (County)"
        if s.lower().startswith("fastest for your route:"):
            parts = s.split(":", 1)[1].strip()
            idx = parts.rfind(" (")
            if idx != -1 and parts.endswith(")"):
                city = parts[:idx].strip()
                county = parts[idx+2:-1].strip()
                return county, city, True
            # Fallback: if only county provided
            return parts, None, True

        # Check for "Fastest route through CountyName"
        if s.lower().startswith("fastest route through"):
            county_part = s[len("fastest route through"):].strip()
            return county_part, None, True

        # Otherwise expect format like "CityName (CountyName)" (may have leading spaces)
        idx = s.rfind(" (")
        if idx != -1 and s.endswith(")"):
            city = s[:idx].strip()
            county = s[idx+2:-1].strip()
            return county, city, False

        # If the cleaned selection matches a county name, return it
        if s in counties:
            return s, None, False

        return None, None, False
    
    start_county, start_city, start_wants_fastest = parse_selection(start_selection)
    end_county, end_city, end_wants_fastest = parse_selection(end_selection)
    
    # Show selection info
    if start_city and start_county:
        if start_wants_fastest:
            st.caption(f"Starting from fastest route: {start_city} in {start_county} County")
        else:
            st.caption(f"📍 Starting from: {start_city} in {start_county} County")

    if end_city and end_county:
        if end_wants_fastest:
            st.caption(f"Ending at fastest route: {end_city} in {end_county} County")
        else:
            st.caption(f"📍 Ending at: {end_city} in {end_county} County")

with col2:
    # Must-visit locations with same structure
    st.markdown("**⭐ Must-visit locations (in order)**")
    
    num_must_visit = st.number_input("How many locations to visit?", 
                                     min_value=0, max_value=10, value=0, 
                                     key="num_must_visit")
    
    must_visit_selections = []
    must_visit_counties = []
    must_visit_cities = []
    
    if num_must_visit > 0:
        for i in range(num_must_visit):
            selection = st.selectbox(
                f"Must-visit #{i+1}", 
                location_options, 
                key=f"must_visit_{i}"
            )
            must_visit_selections.append(selection)
            
            county, city, want_fastest = parse_selection(selection)
            if county:
                must_visit_counties.append(county)
                must_visit_cities.append(city)
    
    optimize_route = st.checkbox("Optimize route for fastest travel time", 
                                 help="Reorders must-visit counties to minimize total drive time")
    
# Map display controls
st.sidebar.header("Map Settings")
show_map = st.sidebar.checkbox("Show map of Washington counties", value=True)
show_edges = st.sidebar.checkbox("Show county connections", value=True)
show_labels = st.sidebar.checkbox("Show county labels", value=True)

BFS_path = None
city_detour_info = None

# Single button for finding path
if st.button("Find Shortest Path", type="primary"):
    st.session_state.button_clicked = True
    
    if not start_county or not end_county:
        st.warning("⚠️ Please select both start and end locations...")
    elif start_county == end_county and not start_city and not end_city:
        st.warning("⚠️ Start and end counties are the same...")
    else:
        with st.spinner("Finding the best route..."):
            if optimize_route and must_visit_counties:
                # Use optimal route finding
                st.info(f"Optimizing route to visit {len(must_visit_counties)} locations in the fastest order...")
                BFS_path = find_optimal_route(wa_graph, start_county, end_county, must_visit_counties)
            else:
                # Use traditional ordered route
                route_points = list(must_visit_counties) + [end_county]
                prev = start_county
                full_path = []
                path_not_found = False

                for target in route_points:
                    subpath = bfs_path(wa_graph, prev, target)
                    if subpath is None:
                        path_not_found = True
                        break
                    if not full_path:
                        full_path.extend(subpath)
                    else:
                        full_path.extend(subpath[1:])
                    prev = target

                BFS_path = None if path_not_found else full_path

if BFS_path is None and st.session_state.get('button_clicked'):
    st.error("❌ Path not found! Counties may not be connected.")
elif BFS_path is not None:
        # Show optimization info if used
        if optimize_route and must_visit_counties:
            st.success("✅ Optimized Route Found!")
            st.info("ℹ️ Must-visit counties were reordered for fastest travel time")
        else:
            st.success("✅ Path Found!")
        
        # Display route in a nice format
        st.subheader("Your Route")
        route_display = " ➡️ ".join([f"**{county}**" if county in must_visit_counties else county for county in BFS_path])
        st.markdown(route_display)

        # Route summary in columns
        col1, col2, col3 = st.columns(3)
        
        visited_counties = BFS_path
        # Build route-specific city selections and compute fastest cities for the route
        route_cities = {}
        if start_city:
            route_cities[start_county] = start_city
        if end_city:
            route_cities[end_county] = end_city
        # incorporate any city choices from must-visit selections
        for c, city in zip(must_visit_counties, must_visit_cities):
            if city:
                route_cities[c] = city
        route_fastest_cities = calculate_route_with_fastest_cities(visited_counties, route_cities, cities_by_county)
        total_stops = len(visited_counties)
        must_in_route = [c for c in must_visit_counties if c in visited_counties]
        
        # Calculate total drive time with city-specific times (seconds)
        total_drive_time = 0
        detailed_segments = []
        
        for i in range(len(visited_counties) - 1):
            current_county = visited_counties[i]
            next_county = visited_counties[i + 1]
            
            current_city = route_fastest_cities.get(current_county)
            next_city = route_fastest_cities.get(next_county)
            
            # Base county-to-county time
            segment_time = get_drive_time(current_county, next_county)
            
            # Add intra-county time if we have specific cities
            if current_city and next_city:
                city_time = get_city_drive_time(current_city, next_city)
                if city_time is None:
                    # Different counties, use base time
                    total_drive_time += segment_time
                else:
                    # Same county, use city-to-city time
                    total_drive_time += city_time
                    segment_time = city_time
            else:
                total_drive_time += segment_time
            
            detailed_segments.append({
                'from_county': current_county,
                'to_county': next_county,
                'from_city': current_city,
                'to_city': next_city,
                'time': segment_time
            })
        
        with col1:
            st.metric("Total Counties", total_stops)
        with col2:
            h = total_drive_time // 3600
            m = (total_drive_time % 3600) // 60
            s = total_drive_time % 60
            st.metric("Drive Time", f"{h}h {m}m {s}s")
        with col3:
            st.metric("Must-Visit Included", len(must_in_route))

        # Show highways used with actual drive times
        if detailed_segments:
            st.subheader("🛣️ Route Segments")
            
            # Create a nice table for the route
            for idx, segment in enumerate(detailed_segments, 1):
                t = int(segment['time']) if segment['time'] is not None else 0
                h = t // 3600
                m = (t % 3600) // 60
                s = t % 60
                if h > 0:
                    time_str = f"{h}h {m}m {s}s"
                elif m > 0:
                    time_str = f"{m}m {s}s"
                else:
                    time_str = f"{s}s"
                
                # Build from/to strings with cities
                from_str = f"{segment['from_city']} ({segment['from_county']} Co.)" if segment['from_city'] else segment['from_county']
                to_str = f"{segment['to_city']} ({segment['to_county']} Co.)" if segment['to_city'] else segment['to_county']
                
                # Get highway info
                highways = []
                if segment['from_county'] in wa_highway_connections:
                    data = wa_highway_connections[segment['from_county']]
                    for city, hwy_dict in data['connections'].items():
                        for highway, destinations in hwy_dict.items():
                            for dest in destinations:
                                if f"({segment['to_county']} Co.)" in dest or f"({segment['to_county']})" in dest:
                                    highways.append(highway)
                highways = sorted(set(highways))
                highways_str = ", ".join(highways) if highways else "Local roads"
                
                col1, col2, col3 = st.columns([2, 3, 1])
                with col1:
                    st.markdown(f"**{idx}. {from_str}** → **{to_str}**")
                with col2:
                    st.markdown(f"`{highways_str}`")
                with col3:
                    st.markdown(f"⏱️ *{time_str}*")

        # Show county details
        st.subheader("📍 County Details")
        for county in visited_counties:
            # Check if it's a must-visit
            is_must_visit = county in must_visit_counties
            title = f"⭐ {county}" if is_must_visit else f"📍 {county}"
            
            with st.expander(title):
                if county in wa_highway_connections:
                    data = wa_highway_connections[county]
                    st.write(f"**Major cities:** {', '.join(data['major_cities'])}")
                    
                    # Show the fastest city for this route
                    if county in route_fastest_cities:
                        st.info(f"Fastest city for your route: **{route_fastest_cities[county]}**")
                    
                    st.write("**Highway connections:**")
                    for city, highways in data['connections'].items():
                        st.write(f"*From {city}:*")
                        for highway, destinations in highways.items():
                            st.write(f"  • {highway}: {', '.join(destinations)}")
                else:
                    st.write("No detailed information available.")

        # Show the map with route
        if show_map:
            st.subheader("Route Map")
            try:
                deck = show_interactive_map(wa_graph, county_coords, route=visited_counties, 
                                          show_edges=show_edges, show_labels=show_labels, 
                                          geojson=geojson, route_cities=route_fastest_cities)
                if deck is not None:
                    st.pydeck_chart(deck)
                else:
                    fig = plot_map(wa_graph, county_coords, route=visited_counties, 
                                 show_edges=show_edges, show_labels=show_labels,
                                 geojson=geojson, route_cities=route_fastest_cities)
                    st.pyplot(fig)
            except Exception as e:
                st.error(f"Error drawing map: {e}")

# Preview map without route
if show_map and BFS_path is None:
    st.subheader("Washington State Counties")
    try:
        deck = show_interactive_map(wa_graph, county_coords, route=None, 
                                   show_edges=show_edges, show_labels=show_labels,
                                   geojson=geojson)
        if deck is not None:
            st.pydeck_chart(deck)
        else:
            fig = plot_map(wa_graph, county_coords, route=None, 
                         show_edges=show_edges, show_labels=show_labels,
                         geojson=geojson)
            st.pyplot(fig)
    except Exception as e:
        st.error(f"Error drawing map preview: {e}")

# Add footer with instructions
st.sidebar.markdown("---")
st.sidebar.info("""
**How to use:**
1. Select your start and end counties
2. Optionally add must-visit counties
3. Click 'Find Shortest Path'
4. View your route with highway information

**Tip:** Download 'wa_counties.geojson' for county borders!
""")