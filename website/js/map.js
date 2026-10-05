/**
 * SONAR // Leaflet Geospatial Concert Turnout Map
 * Displays worldwide concert tour turnouts with interactive popups & dynamic filtering.
 * Defaults to clean, open, watermark-free ESRI World Dark Gray Canvas tiles,
 * with built-in support for CARTO basemap API keys and alternative providers.
 */

window.MapEngine = {
  map: null,
  markerLayer: null,
  baseTileLayers: [],
  concerts: [],
  activeProvider: 'esri',

  // Artist color mappings
  artistColors: {
    "Taylor Swift": "#EC4899",
    "Coldplay": "#06B6D4",
    "Ed Sheeran": "#F59E0B",
    "Beyonce": "#8B5CF6",
    "Harry Styles": "#10B981",
    "The Weeknd": "#EF4444",
    "U2": "#6366F1",
    "Elton John": "#EAB308",
    "Oasis": "#3B82F6",
    "Bad Bunny": "#F97316"
  },

  initMap(concerts) {
    this.concerts = concerts || [];
    const mapContainer = document.getElementById('concert-map');
    if (!mapContainer) return;

    // Center map view globally
    this.map = L.map('concert-map', {
      center: [25.0, 10.0],
      zoom: 2,
      minZoom: 2,
      maxZoom: 12,
      zoomControl: true,
      attributionControl: false
    });

    // Load active provider from localStorage or default to ESRI
    const savedProvider = localStorage.getItem('sonar_basemap_provider') || 'esri';
    this.setBasemap(savedProvider);

    this.markerLayer = L.layerGroup().addTo(this.map);
    this.renderMarkers(this.concerts);
    this.setupFilterListeners();
  },

  setBasemap(provider) {
    // Remove existing tile layers
    this.baseTileLayers.forEach(layer => {
      if (this.map.hasLayer(layer)) {
        this.map.removeLayer(layer);
      }
    });
    this.baseTileLayers = [];
    this.activeProvider = provider;
    localStorage.setItem('sonar_basemap_provider', provider);

    const providerSelect = document.getElementById('map-basemap-provider');
    if (providerSelect && providerSelect.value !== provider) {
      providerSelect.value = provider;
    }

    if (provider === 'carto') {
      const cartoKey = localStorage.getItem('carto_api_key') || '';
      let url = 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png';
      if (cartoKey.trim()) {
        url += `?api_key=${encodeURIComponent(cartoKey.trim())}`;
      }
      const cartoLayer = L.tileLayer(url, {
        subdomains: 'abcd',
        maxZoom: 19
      }).addTo(this.map);
      this.baseTileLayers.push(cartoLayer);

    } else if (provider === 'osm_dark') {
      const osmLayer = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        className: 'osm-dark-tiles'
      }).addTo(this.map);
      this.baseTileLayers.push(osmLayer);

    } else {
      // Default: ESRI World Dark Gray Canvas (100% Free, Zero Watermarks, Clean Obsidian)
      const esriBase = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}', {
        maxZoom: 16
      }).addTo(this.map);

      const esriLabels = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Reference/MapServer/tile/{z}/{y}/{x}', {
        maxZoom: 16
      }).addTo(this.map);

      this.baseTileLayers.push(esriBase, esriLabels);
    }
  },

  renderMarkers(filteredList) {
    if (!this.markerLayer) return;
    this.markerLayer.clearLayers();

    filteredList.forEach(c => {
      if (!c.latitude || !c.longitude || (c.latitude === 0 && c.longitude === 0)) return;

      const radius = Math.min(16, Math.max(5, (c.attendance / 6000)));
      const color = this.artistColors[c.artist] || '#6366F1';

      const circle = L.circleMarker([c.latitude, c.longitude], {
        radius: radius,
        fillColor: color,
        color: '#FFFFFF',
        weight: 1,
        opacity: 0.8,
        fillOpacity: 0.7
      });

      const popupContent = `
        <div class="map-popup">
          <div class="map-popup-title">${c.artist}</div>
          <div class="map-popup-sub">${c.venue} — ${c.city}, ${c.country}</div>
          <div class="map-popup-grid">
            <div class="map-popup-item">Turnout: <strong>${c.attendance.toLocaleString()}</strong></div>
            <div class="map-popup-item">Occupancy: <strong>${c.occupancy_rate}%</strong></div>
            <div class="map-popup-item">Gross USD: <strong>$${(c.gross_usd / 1e6).toFixed(2)}M</strong></div>
            <div class="map-popup-item">Avg Ticket: <strong>$${c.avg_ticket_price.toFixed(2)}</strong></div>
            <div class="map-popup-item">Date: <strong>${c.date}</strong></div>
            <div class="map-popup-item">Tour: <strong>${c.tour}</strong></div>
          </div>
        </div>
      `;

      circle.bindPopup(popupContent);
      this.markerLayer.addLayer(circle);
    });
  },

  setupFilterListeners() {
    const artistSelect = document.getElementById('map-filter-artist');
    const continentSelect = document.getElementById('map-filter-continent');
    const venueSelect = document.getElementById('map-filter-venue');
    const basemapSelect = document.getElementById('map-basemap-provider');

    const applyFilter = () => {
      const selectedArtist = artistSelect ? artistSelect.value : 'all';
      const selectedContinent = continentSelect ? continentSelect.value : 'all';
      const selectedVenue = venueSelect ? venueSelect.value : 'all';

      const filtered = this.concerts.filter(c => {
        const matchArtist = selectedArtist === 'all' || c.artist === selectedArtist;
        const matchContinent = selectedContinent === 'all' || c.continent === selectedContinent;
        const matchVenue = selectedVenue === 'all' || c.venue_type === selectedVenue;
        return matchArtist && matchContinent && matchVenue;
      });

      this.renderMarkers(filtered);
    };

    if (artistSelect) artistSelect.addEventListener('change', applyFilter);
    if (continentSelect) continentSelect.addEventListener('change', applyFilter);
    if (venueSelect) venueSelect.addEventListener('change', applyFilter);

    if (basemapSelect) {
      basemapSelect.addEventListener('change', (e) => {
        this.setBasemap(e.target.value);
      });
    }
  }
};
