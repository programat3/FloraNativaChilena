import pandas as pd
import math

def euclidean_distance(point1, point2):
  """Calculates the Euclidean distance between two points."""
  x1, y1 = point1
  x2, y2 = point2
  return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def shortest_distance(point, list_of_points):
  """Calculates the shortest distance between a point and a list of points."""
  if not list_of_points:
    return None  # Return None if the list is empty
  punto_menor = list_of_points[0]  # Initialize with the first point
  min_distance = float('inf') # Initialize with a large value
  for other_point in list_of_points:
      distance = euclidean_distance(point, other_point)
      min_distance = min(min_distance, distance)
      punto_menor = other_point if distance == min_distance else punto_menor
  return min_distance, punto_menor

def find_nearest_subZone(point):
    """
    Encuentra la subzona más cercana a un punto dado.
    
    Args:
        point (tuple): Un punto representado como una tupla (x, y).    
    Returns:
        subZona: La subzona más cercana al punto dado.
    """
    df = pd.read_json("./data/coordinates_zona.json")
    df["coordinates"] = list(zip(df["latitud_s"], df["longitud_w"]))
    coordinates = df["coordinates"].tolist()
    cercano, point = shortest_distance(point, coordinates)    
    #Find subzone with the closest point
    closest = df.iloc[coordinates.index(point)]
    cercano = {
        "name": closest["zona"],
        "coordinates": closest["coordinates"]
    }
    return cercano

print(find_nearest_subZone((25.8, 69.5))) # Example usage, replace with actual coordinates