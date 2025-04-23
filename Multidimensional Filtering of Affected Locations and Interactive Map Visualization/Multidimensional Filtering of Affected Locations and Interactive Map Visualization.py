import os

def check_files():
    files = [
        r"D:\Visual Analysis of Typhoons\data\typhoon_data.csv",
        r"D:\Visual Analysis of Typhoons\data\Ningbo.json"
    ]
    for file in files:
        if not os.path.exists(file):
            raise FileNotFoundError(f"找不到文件: {file}")

def generate_html():
    html_content = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Typhoon Khanun Impact Map in Ningbo</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
    <style>
        body {
            margin: 0;
            padding: 0;
        }
        #map {
            height: 100vh;
            width: 100%;
        }
        .legend {
            padding: 15px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 0 15px rgba(0,0,0,0.2);
            max-height: 500px;
            overflow-y: auto;
        }
        .legend-title {
            font-size: 16px;
            font-weight: bold;
            margin-bottom: 15px;
            color: #333;
            border-bottom: 2px solid #3498db;
            padding-bottom: 5px;
        }
        .popup-content {
            min-width: 320px;
            max-width: 420px;
            line-height: 1.8;
            padding: 12px;
            font-size: 14px;
            color: #2c3e50;
        }
        .popup-title {
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 15px;
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 8px;
            text-align: center;
        }
        .popup-item {
            margin: 12px 0;
            padding: 8px;
            background-color: #f8f9fa;
            border-radius: 6px;
        }
        .popup-item strong {
            color: #34495e;
            font-size: 15px;
            display: block;
            margin-bottom: 4px;
        }
        .leaflet-popup-content {
            margin: 15px;
        }
        .leaflet-popup-content-wrapper {
            border-radius: 8px;
            box-shadow: 0 3px 14px rgba(0,0,0,0.2);
        }
        .leaflet-popup-tip-container {
            margin-top: -1px;
        }
    </style>
</head>
<body>
    <div id="map"></div>
    <script>
        const categories = [
            "Population", 
            "Infrastructure", 
            "Buildings", 
            "Industry", 
            "Public Services", 
            "Agriculture and Fishery", 
            "Service Industry", 
            "Land Resources", 
            "Ecological Resources", 
            "Water Resources", 
            "Biological Resources", 
            "Mineral Resources"
        ];

        const map = L.map('map').setView([29.8683, 121.5440], 10);
        
        L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
            attribution: '&copy; CartoDB',
            maxZoom: 18
        }).addTo(map);

        let markers = [];

        const legend = L.control({position: 'topright'});
        legend.onAdd = function(map) {
            const div = L.DomUtil.create('div', 'legend');
            div.innerHTML = '<div class="legend-title">Impact Category Filter</div>';
            
            div.innerHTML += `
                <div style="margin-bottom: 10px;">
                    <input type="checkbox" id="selectAll" onchange="toggleAll(this.checked)">
                    <label for="selectAll">Select All/None</label>
                </div>
            `;
            
            categories.forEach(category => {
                div.innerHTML += `
                    <div style="margin: 5px 0;">
                        <input type="checkbox" id="${category}" onchange="filterMarkers()">
                        <label for="${category}">${category}</label>
                    </div>
                `;
            });
            return div;
        };
        legend.addTo(map);

        fetch('D:/Visual Analysis of Typhoons/data/Ningbo.json')
            .then(response => response.json())
            .then(data => {
                L.geoJSON(data, {
                    style: {
                        color: '#3388ff',
                        weight: 2,
                        opacity: 0.8,
                        fillColor: '#3388ff',
                        fillOpacity: 0.2,
                        dashArray: null
                    }
                }).addTo(map);
            })
            .catch(error => {
                console.error('Error loading GeoJSON:', error);
                alert('Failed to load Ningbo boundary data');
            });

        fetch('D:/Visual Analysis of Typhoons/data/typhoon_data.csv')
            .then(response => response.text())
            .then(data => {
                const rows = data.split('\\n').slice(1);
                rows.forEach(row => {
                    if (!row.trim()) return;
                    
                    let cols = [];
                    let current = '';
                    let inQuotes = false;
                    
                    for(let char of row) {
                        if (char === '"') {
                            inQuotes = !inQuotes;
                        } else if (char === ',' && !inQuotes) {
                            cols.push(current);
                            current = '';
                        } else {
                            current += char;
                        }
                    }
                    cols.push(current);

                    if (cols.length < 8) return;

                    const location = cols[0].replace(/^"|"$/g, '');
                    const lat = parseFloat(cols[1]);
                    const lng = parseFloat(cols[2]);
                    
                    if (isNaN(lat) || isNaN(lng)) return;

                    const start_date = cols[3];
                    const end_date = cols[4];
                    const details = cols[5];
                    const admin_level = cols[6];
                    const categoryList = cols[7]
                        .replace(/^"|"$/g, '')
                        .split(',')
                        .map(cat => cat.trim())
                        .filter(cat => cat);

                    const marker = L.marker([lat, lng])
                        .bindPopup(`
                            <div class="popup-content">
                                <div class="popup-title">${location}</div>
                                <div class="popup-item">
                                    <strong>⏰ Time Range</strong>
                                    ${start_date} to ${end_date}
                                </div>
                                <div class="popup-item">
                                    <strong>📝 Details</strong>
                                    ${details}
                                </div>
                                <div class="popup-item">
                                    <strong>🏢 Admin Level</strong>
                                    ${admin_level}
                                </div>
                                <div class="popup-item">
                                    <strong>🏷️ Impact Categories</strong>
                                    ${categoryList.join(', ')}
                                </div>
                            </div>
                        `, {
                            maxWidth: 420,
                            className: 'custom-popup'
                        });
                    
                    marker.categories = categoryList;
                    markers.push(marker);
                    marker.addTo(map);
                });
            })
            .catch(error => {
                console.error('Error loading CSV:', error);
                alert('Failed to load data. Please check the console for details.');
            });

        window.filterMarkers = function() {
            try {
                const selectedCategories = categories.filter(category => 
                    document.getElementById(category) && 
                    document.getElementById(category).checked
                );

                markers.forEach(marker => {
                    if (!marker.categories) return;
                    
                    const hasSelectedCategory = marker.categories.some(category => {
                        const trimmedCategory = category.trim();
                        return selectedCategories.includes(trimmedCategory);
                    });
                    
                    if (selectedCategories.length === 0 || hasSelectedCategory) {
                        marker.addTo(map);
                    } else {
                        marker.remove();
                    }
                });
            } catch (error) {
                console.error('Filter error:', error);
            }
        };

        window.toggleAll = function(checked) {
            categories.forEach(category => {
                const checkbox = document.getElementById(category);
                if (checkbox) {
                    checkbox.checked = checked;
                }
            });
            filterMarkers();
        };
    </script>
</body>
</html>'''

    # 将HTML内容写入文件
    with open('typhoon_map/index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

if __name__ == '__main__':
    try:
        check_files()
        os.makedirs('typhoon_map', exist_ok=True)
        generate_html()
        print("HTML文件已生成在 typhoon_map/index.html")
    except Exception as e:
        print(f"错误: {e}")