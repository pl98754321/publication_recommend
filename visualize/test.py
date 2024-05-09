import json

def transform_data(input_data):
    transformed_data = []
    
    # Extract 'from' affiliation
    from_affiliation = input_data['affilations'][0]
    if from_affiliation['lat'] is not None and from_affiliation['lng'] is not None:
        from_data = {
            "from": {
                "name": from_affiliation['affiliation'],
                "coordinates": [
                    from_affiliation['lng'],
                    from_affiliation['lat']
                ]
            }
        }
    else:
        return []

    transformed_data.append(from_data)

    # Extract 'to' affiliations from node_graph
    node_graph = input_data.get('node_graph', {}).get('node', [])
    for node in node_graph:
        for to_affiliation in node['affilations']:
            if to_affiliation['lat'] is not None and to_affiliation['lng'] is not None:
                to_data = {
                    "to": {
                        "name": to_affiliation['affiliation'],
                        "coordinates": [
                            to_affiliation['lng'],
                            to_affiliation['lat']
                        ]
                    }
                }
                transformed_data.append({**from_data, **to_data})

    return transformed_data[1:]

input_json = '''
{
  "title": "Machine Learning Based Design of Railway Prestressed Concrete Sleepers",
  "id": 13960,
  "affilations": [
    {
      "lat": 13.7389,
      "lng": 100.5284,
      "affiliation": "Chulalongkorn University"
    },
    {
      "lat": null,
      "lng": null,
      "affiliation": "University of Birmingham"
    },
    {
      "lat": null,
      "lng": null,
      "affiliation": "University of Wollongong"
    }
  ],
  "node_graph": {
    "node": [
      {
        "title": "The Impact of Data-Complexity and Team Characteristics on Performance in the Classification Model: Findings From a Collaborative Platform",
        "id": 12299,
        "affilations": [
          {
            "lat": 37.6170,
            "lng": -122.3834,
            "affiliation": "Chulalongkorn Business School"
          }
        ]
      },
      {
        "title": "Digital-Twins towards Cyber-Physical Systems: A Brief Survey",
        "id": 14112,
        "affilations": [
          {
            "lat": 13.7389,
            "lng": 100.5284,
            "affiliation": "Chulalongkorn University"
          },
          {
            "lat": 37.6170,
            "lng": -122.3834,
            "affiliation": "Atria Institute of Technology"
          },
          {
            "lat": 37.6170,
            "lng": -122.3834,
            "affiliation": "King Mongkut's University of Technology North Bangkok"
          },
          {
            "lat": 37.6170,
            "lng": -122.3834,
            "affiliation": "Pathumwan Institute of Technology"
          }
        ]
      },
      {
        "title": "Reliability Quantification of Railway Electrification Mast Structure Considering Buckling",
        "id": 9310,
        "affilations": [
          {
            "lat": 13.7389,
            "lng": 100.5284,
            "affiliation": "Chulalongkorn University"
          },
          {
            "lat": 37.6170,
            "lng": -122.3834,
            "affiliation": "University of Birmingham"
          },
          {
            "lat": 37.6170,
            "lng": -122.3834,
            "affiliation": "Harbin Institute of Technology"
          }
        ]
      }
    ]
  }
}
'''

input_data = json.loads(input_json)
transformed_data = transform_data(input_data)
print(json.dumps(transformed_data, indent=2))
