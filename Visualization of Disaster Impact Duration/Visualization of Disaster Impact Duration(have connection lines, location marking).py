import folium
from folium import plugins
import pandas as pd
from branca.colormap import LinearColormap
# Add the precise boundary of Ningbo
import json

# Data preprocessing
try:
    df = pd.read_csv(r'D:\Visual Analysis of Typhoons\data\typhoon_data.csv', parse_dates=['start_date', 'end_date'])
    df['Impact Days'] = (df['end_date'] - df['start_date']).dt.days + 1
    avg_lat = df['latitude'].mean()
    avg_lng = df['longitude'].mean()
except:
    avg_lat, avg_lng = 26.0, 118.0

# Create the map
m = folium.Map(
    location=[avg_lat, avg_lng],
    zoom_start=7,
    tiles='https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
    attr='CartoDB',
    control_scale=True,
    prefer_canvas=True
)

try:
    # Load Ningbo GeoJSON data
    with open('D:/Visual Analysis of Typhoons/data/Ningbo.json', 'r', encoding='utf-8') as f:
        ningbo_geojson = json.load(f)

    folium.GeoJson(
        ningbo_geojson,
        name='Ningbo',
        style_function=lambda x: {
            'fillColor': '#3388ff',
            'color': '#3388ff',
            'weight': 2,
            'fillOpacity': 0.2
        },
        tooltip='Ningbo'
    ).add_to(m)
except Exception as e:
    print(f"Failed to load Ningbo boundary data: {e}")

# Create a color scale
colormap = LinearColormap(['#FFEDA0', '#FEB24C', '#FC4E2A'],
                         vmin=df['Impact Days'].min(),
                         vmax=df['Impact Days'].max()).to_step(5)
colormap.caption = 'Typhoon Impact Duration (days)'
m.add_child(colormap)

# Add markers
# Add a marker for the center of Ningbo after creating the map
ningbo_center = [29.87, 121.54]  # Coordinates of the center of Ningbo

# Modify the marker addition part to optimize the visual effect
for _, row in df.iterrows():
    location = [row['latitude'], row['longitude']]

    # Add a dashed connecting line
    folium.PolyLine(
        locations=[ningbo_center, location],
        color='#666666',  # Softer gray
        weight=1.5,  # Slightly thinner line
        opacity=0.7,
        dash_array='5, 3'  # Dashed style
    ).add_to(m)

    # Marker for the disaster - affected location (optimized style)
    folium.CircleMarker(
        location=location,
        radius=8,
        color=colormap(row['Impact Days']),
        fill=True,
        fill_color=colormap(row['Impact Days']),
        fill_opacity=0.9,  # Increase fill transparency
        popup=folium.Popup(f"""
            <div style="width:300px;font-family:Microsoft YaHei">
                <h4 style="color:#2c7bb6;margin:0">{row['location']}</h4>
                <p style="margin:5px 0">Impact Days: <b>{row['Impact Days']} days</b></p>
                <hr style="margin:5px 0">
                <p style="font-size:0.9em">{row['details']}</p>
            </div>
        """, max_width=300),
        tooltip=f"{row['location']}",
        z_index_offset=100
    ).add_to(m)

    # Label for the location name (optimized style)
    folium.Marker(
        location=[location[0]-0.015, location[1]],  # Fine - tune the position
        icon=folium.DivIcon(
            html=f"""
            <div style="
                font-size:10px;
                color:#444;
                font-weight:500;
                background:rgba(255,255,255,0.85);
                padding:2px 5px;
                border-radius:3px;
                white-space:nowrap;
                border:1px solid #ddd;
                font-family:Microsoft YaHei
            ">{row["location"]}</div>
            """
        ),
        z_index_offset=200
    ).add_to(m)

# Marker for the center of Ningbo
folium.Marker(
    location=[29.87, 121.54],
    icon=folium.DivIcon(
        html='<div style="font-size:14px;color:#00AA00;font-weight:bold;background:rgba(255,255,255,0.9);padding:3px 8px;border-radius:4px;border:1px solid #00AA00;font-family:Arial;white-space:nowrap">Ningbo</div>'
    ),
    z_index_offset=400
).add_to(m)

folium.CircleMarker(
    location=ningbo_center,
    radius=14,
    color='#00AA00',
    fill=True,
    fill_color='#00AA00',
    fill_opacity=1,
    popup='Ningbo City Center',
    weight=3,
    z_index_offset=300
).add_to(m)

# Add controls
plugins.Fullscreen().add_to(m)
plugins.MousePosition().add_to(m)
# Remove the following line to remove the MiniMap control in the lower - right corner
# plugins.MiniMap().add_to(m)

# Resource guarantee
m.get_root().html.add_child(folium.Element('''
<script>
if(typeof L === 'undefined'){
    document.write('<script src="https://cdn.bootcdn.net/ajax/libs/leaflet/1.9.4/leaflet.js"><\\/script>');
}
</script>
'''))

# Save the file
output_path = 'Visualization of Disaster Impact Duration(have connection lines, location marking).html'
m.save(output_path)
print(f"The map has been saved to: {output_path}")
    