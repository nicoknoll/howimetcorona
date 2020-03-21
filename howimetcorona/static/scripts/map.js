document.addEventListener("DOMContentLoaded", function() {
  const points = window.data.points || [];
  const riskPoints = window.data.riskPoints || [];

  // Moabit
  let initialLat = 52.52635;
  let initialLng = 13.33903;

  if (points.length) {
     initialLat = points[0].lat;
     initialLng = points[0].lng;
  }

  const map = L.map('map').setView([initialLat, initialLng], 15);

  L.tileLayer('http://a.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
  }).addTo(map);

  const linePoints = points.map((point) => [point.lat, point.lng]);
  const polyline = L.polyline(linePoints, {color: 'green'}).addTo(map);
  map.fitBounds(polyline.getBounds());

  riskPoints.forEach((point) => {
    L.circleMarker([point.lat, point.lng], {
      color: 'red'
    }).addTo(map);
  });
});
