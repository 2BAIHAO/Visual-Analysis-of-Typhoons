import pandas as pd
import folium
from folium.plugins import TimestampedGeoJson, Fullscreen, MousePosition 
from datetime import datetime, timedelta

def process_data(csv_path):
    """Data preprocessing"""
    df = pd.read_csv(csv_path, parse_dates=['start_date', 'end_date'])
    
    typhoon_center = [26.7, 124.2]  # Coordinates of Ningbo City
    # Calculate the duration and filter invalid data
    df['duration'] = (df['end_date'] - df['start_date']).dt.days + 1
    df = df[df['duration'] > 0]
    
    # Generate geographical features
    features = []
    for _, row in df.iterrows():
        dates = [row['start_date'] + timedelta(days=i) for i in range(row['duration'])]
        
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [row['longitude'], row['latitude']]
            },
            "properties": {
                "times": [d.strftime('%Y-%m-%dT%H:%M:%S') for d in dates],
                "location": row['location'],
                "style": {
                    "color": "#1976D2",
                    "fillColor": "#1976D2",
                    "opacity": 0.8,
                    "fillOpacity": 0.6,
                    "radius": 8
                },
                "popup": f"""
                    <div style="width:400px; font-family:Arial">
                        <h4 style="color:#0D47A1; margin:0; font-size:25px">{row['location']}</h4>
                        <p style="margin:10px 0; font-size:21px">
                            <b>Date:</b> {row['start_date'].date()} - {row['end_date'].date()}<br>
                            <b>Admin Level:</b> {row['admin_level']}
                        </p>
                        <hr style="margin:12px 0">
                        <p style="font-size:15px; line-height:1.6; word-wrap:break-word; word-break:break-word; white-space:pre-wrap">{row['details']}</p>
                    </div>
                """
            }
        })
            
    # Add the location of Ningbo City (displayed throughout the time period)
    features.insert(0, {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": typhoon_center},
        "properties": {
            "times": ["2023-07-31T00:00:00", "2023-08-06T23:59:59"],
            "style": {"color": "#FF0000", "fillColor": "#FF0000", "radius": 10}
        }
    })
    
    return {'type': 'FeatureCollection', 'features': features}

def create_map(geojson_data):
    """Create a map that matches the example image effect"""
    # Initialize the map (gray map without labels)
    m = folium.Map(
        location=[29.95, 121.5],
        zoom_start=11,
        tiles='CartoDB.PositronNoLabels',
        control_scale=True
    )
    
    '''
    label_group = folium.FeatureGroup(name='Location Labels')
    for feature in geojson_data['features']:
        if feature['geometry']['type'] == 'Point' and 'location' in feature['properties']:
            lon, lat = feature['geometry']['coordinates']
            label_group.add_child(folium.Marker(
                location=[lat, lon],
                icon=folium.DivIcon(
                    html=f'<div style="font-size:9px;color:#1A237E;margin-top:12px">{feature["properties"]["location"]}</div>'
                )
            ))
    label_group.add_to(m)
    '''

    # Add the precise boundary of Ningbo City
    try:
        import json
        with open(r'D:\Visual Analysis of Typhoons\data\Ningbo.json', 'r', encoding='utf-8') as f:
            ningbo_geojson = json.load(f)
        
        # Add the boundary layer
        folium.GeoJson(
            ningbo_geojson,
            name='Ningbo',
            style_function=lambda x: {
                'fillColor': '#3388ff',
                'color': '#3388ff',
                'weight': 2,
                'fillOpacity': 0.3,
                'dashArray': '5, 5'  # Add a dashed line effect
            },
            tooltip=folium.GeoJsonTooltip(fields=['name'], aliases=['City:'])
        ).add_to(m)
        
        # Add the text label for Ningbo City
        folium.Marker(
            location=[29.87, 121.54],
            icon=folium.DivIcon(
                html='<div style="font-size: 14px; color: #3388ff; font-weight: bold;">Ningbo</div>'
            ),
            z_index_offset=1000
        ).add_to(m)
    except Exception as e:
        print(f"Failed to load Ningbo boundary data: {e}")

    # Add the timeline layer
    timestamped_layer = TimestampedGeoJson(
        geojson_data,
        period='P1D',
        transition_time=500,
        date_options='YYYY/MM/DD',
        add_last_point=True,
        loop=False  
    ).add_to(m)
    
    # Add controls
    m.get_root().html.add_child(folium.Element('''
    <div style="position: fixed;
        top: 20px;
        left: 20px;
        z-index: 1000;
        background: rgba(255,255,255,0.9);
        padding: 8px;
        border-radius: 4px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.2);
        border: 1px solid #BDBDBD">
        <input type="date" 
            id="dateControl" 
            min="2023-07-31" 
            max="2023-08-06"
            style="width: 150px; 
                   padding: 4px;
                   border: 1px solid #9E9E9E;
                   border-radius: 3px">
    </div>
    <script>
        
        function setupSync() {
            const timeLayer = document.querySelector('.timestamped-geojson');
            const dateInput = document.getElementById('dateControl');
            
            // Two-way synchronization
            dateInput.addEventListener('change', function() {
                const selectedDate = new Date(this.value);
                timeLayer.setTime(selectedDate.getTime());
            });
            
            timeLayer.addEventListener('timechange', function(e) {
                const currentDate = new Date(e.detail.timestamp);
                dateInput.valueAsDate = currentDate;
            });
            
            // Initial synchronization
            const firstDate = new Date(timeLayer._geojson.features[0].properties.times[0]);
            dateInput.valueAsDate = firstDate;
            dateInput.min = firstDate.toISOString().split('T')[0];
            
            const lastFeature = timeLayer._geojson.features[timeLayer._geojson.features.length-1];
            const lastDate = new Date(lastFeature.properties.times[lastFeature.properties.times.length-1]);
            dateInput.max = lastDate.toISOString().split('T')[0];
        }
        
        document.addEventListener('DOMContentLoaded', setupSync);
    </script>
    '''))

    # Add other controls
    Fullscreen(position='topright').add_to(m)
    MousePosition(position='bottomleft').add_to(m)
    
    return m

if __name__ == "__main__":
    # 使用绝对路径访问数据文件
    data = process_data(r"D:\Visual Analysis of Typhoons\data\typhoon_data.csv")
    map_obj = create_map(data)
    map_obj.save("Interactive spatiotemporal mapping of disaster locations.html")
    print("Interactive spatiotemporal mapping of disaster locations has been completed!")