// https://github.com/zauberzeug/nicegui/blob/main/examples/map/leaflet.js
export default {
  template: "<div></div>",
  mounted() {
    this.map = L.map(this.$el);
    L.tileLayer("http://{s}.tile.osm.org/{z}/{x}/{y}.png", {
      attribution: '&copy; <a href="https://openstreetmap.org/copyright">OpenStreetMap contributors</a>',
    }).addTo(this.map);
  },
  methods: {
    set_location(latitude, longitude,zoom_level) {
      this.target = L.latLng(latitude, longitude);
      this.map.setView(this.target, zoom_level);
      if (this.marker) {
        this.map.removeLayer(this.marker);
      }
      this.marker = L.marker(this.target);
      this.marker.addTo(this.map);
    },
    set_zoom_level(zoom_level) {
		this.map.setZoom(zoom_level);
	},
    draw_path(path) {
      if (this.pathLayer) {
        this.map.removeLayer(this.pathLayer);  // Remove previous path if any
      }
      this.pathLayer = L.polyline(path, {color: 'red'}).addTo(this.map);
      this.map.fitBounds(this.pathLayer.getBounds());  // Adjust view to fit the path
    }
  },
};