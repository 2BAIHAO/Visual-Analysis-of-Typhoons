import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import numpy as np
from matplotlib.colors import Normalize  
import cartopy.crs as ccrs  
import cartopy.feature as cfeature  
import matplotlib as mpl
from matplotlib.font_manager import FontProperties


# Read and parse the data
data = []
with open(r"D:\Visual Analysis of Typhoons\data\Track data of Typhoon Khanun.txt", "r") as f:
    for line in f:
        if line.startswith("66666"):
            continue
        parts = line.strip().split()
        if len(parts) < 6:
            continue
            
        # Parse the date-time and geographical information
        dt = datetime.strptime(parts[0], "%Y%m%d%H")
        lat = float(parts[2])/10   # Convert to actual latitude
        lon = float(parts[3])/10   # Convert to actual longitude
        wind = int(parts[5])       # Wind speed for marker size
        
        data.append({
            "time": dt,
            "lat": lat,
            "lon": lon,
            "wind": wind
        })

# Convert to numpy array for easier processing
times = np.array([d["time"] for d in data])
lats = np.array([d["lat"] for d in data])
lons = np.array([d["lon"] for d in data])
winds = np.array([d["wind"] for d in data])


# Create a canvas with geographical projection
# Add the following import at the beginning of the file
import matplotlib as mpl
from matplotlib.font_manager import FontProperties

# Add font settings before creating the canvas
# Set the global font to a font that supports Chinese characters
plt.rcParams['font.sans-serif'] = ['SimHei']  # Use SimHei font
plt.rcParams['axes.unicode_minus'] = False  # Solve the problem of minus sign display

# Create the map projection
# Modify the canvas size (originally 14,8, now adjusted to 10,6)
plt.figure(figsize=(10, 6))
ax = plt.axes(projection=ccrs.PlateCarree())

# For special font settings in Cartopy, specify the font using an absolute path
font_path = 'C:/Windows/Fonts/msyh.ttc'  # Microsoft YaHei font
font = FontProperties(fname=font_path, size=12)
# Modify the title and labels to English
ax.set_title("Typhoon Khanun Path 2023", fontproperties=font, pad=20)
ax.set_xlabel("Longitude", fontproperties=font)
ax.set_ylabel("Latitude", fontproperties=font)
ax.set_extent([115, 135, 18, 42], crs=ccrs.PlateCarree())  
# Set the font for Cartopy geographical labels
ax.gridlines(draw_labels=True,
             xformatter=plt.FixedFormatter([]),  # Customize longitude labels
             yformatter=plt.FixedFormatter([]),
             linewidth=0.5,
             color='gray',
             alpha=0.5,
             linestyle='--')

# Add longitude and latitude labels
ax.text(0.5, -0.12, 'Longitude', 
        transform=ax.transAxes,
        ha='center', va='center', 
        fontsize=12, fontfamily='SimHei')

# Modify the position of the latitude label, move it to the left and adjust the font size
ax.text(-0.2, 0.5, 'Latitude',
        transform=ax.transAxes,
        rotation=90, 
        ha='center', va='center',
        fontsize=11)  
        
# Set the color mapping (according to time)
norm = mdates.date2num(times)
cmap = plt.get_cmap("plasma")
colors = cmap((norm - norm.min())/(norm.max() - norm.min()))

# Draw the track line and scatter points
sc = ax.scatter(lons, lats, c=colors, s=winds*2, 
                edgecolor="white", alpha=0.8, zorder=3)
line = ax.plot(lons, lats, color="grey", 
               linewidth=1.5, alpha=0.6, zorder=2)[0]

# Add start and end markers
ax.scatter(lons[0], lats[0], s=120, facecolor="lime", 
           edgecolor="black", label="Start", zorder=4)
ax.scatter(lons[-1], lats[-1], s=120, facecolor="red", 
           edgecolor="black", label="End", zorder=4)

# Add the color bar
# Modify the part of creating the color bar

norm_values = mdates.date2num(times)  # Get the date values
cbar = plt.colorbar(
    plt.cm.ScalarMappable(norm=Normalize(norm_values.min(), norm_values.max()),
                        cmap=cmap),
    ax=ax,
    format=mdates.DateFormatter("%m-%d")  # New formatting
)
cbar.ax.tick_params(length=0)  # Hide the tick marks

cbar.set_label("Time", fontsize=12)
cbar.ax.yaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))

# Set the axis range
lon_pad = (lons.max() - lons.min())*0.1
lat_pad = (lats.max() - lats.min())*0.1
ax.set_xlim(lons.min()-lon_pad, lons.max()+lon_pad)
ax.set_ylim(lats.min()-lat_pad, lats.max()+lat_pad)

# Add geographical information annotations
ax.add_feature(cfeature.LAND, facecolor='#f0f0f0')
ax.add_feature(cfeature.OCEAN, facecolor='#e0f3ff') 
ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.8)
ax.add_feature(cfeature.BORDERS, linestyle=':', linewidth=0.5)

# Provincial borders
province_borders = cfeature.NaturalEarthFeature(
    category='cultural',
    name='admin_1_states_provinces_lines',
    scale='50m',
    facecolor='none'
)
ax.add_feature(province_borders, edgecolor='gray', linewidth=0.5)

# Modify the annotation of Shanghai to English
ax.plot(121.47, 31.23, 'o', color='red', markersize=6, 
        transform=ccrs.PlateCarree())
ax.text(121.97, 31.23, 'Shanghai', fontsize=10, 
        transform=ccrs.PlateCarree())

ax.gridlines(draw_labels=True,  # Automatically annotate longitude and latitude
             linewidth=0.5, 
             color='gray',
             alpha=0.5,
             linestyle='--')

# Set the legend and labels
ax.set_title("Typhoon Khanun Path 2023", fontsize=16, pad=20)
ax.set_xlabel("Longitude", fontsize=12)
ax.set_ylabel("Latitude", fontsize=12)
ax.grid(True, linestyle="--", alpha=0.5)
ax.legend(loc="upper right")
# Output verification
plt.savefig('enhanced_typhoon_path.png', dpi=300, bbox_inches='tight')
# Optimize the layout
plt.tight_layout()
plt.show()