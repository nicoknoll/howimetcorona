document.addEventListener("DOMContentLoaded", function() {
  var points = window.data.points;

  var map = L.map('map').setView([points[0].lat, points[0].lng], 15);

  L.tileLayer('http://a.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
  }).addTo(map);

  points.forEach((point) => {
    console.log([point.lat, point.lng]);
    L.marker([point.lat, point.lng]).addTo(map);
  });
});
