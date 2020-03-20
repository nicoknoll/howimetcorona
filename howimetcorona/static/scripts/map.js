document.addEventListener("DOMContentLoaded", function() {
  const points = window.data.points || [];

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

  points.forEach((point) => {
    L.marker([point.lat, point.lng], {
      icon: L.icon({
        iconSize: [ 25, 41 ],
        iconAnchor: [ 13, 41 ],
        iconUrl: '/static/images/marker-icon.png',
        shadowUrl: '/static/images/marker-shadow.png'
      })
    }).addTo(map);
  });
});
