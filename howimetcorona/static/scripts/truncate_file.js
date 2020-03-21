document.addEventListener("DOMContentLoaded", function() {
  const MAX_DAYS = 14;

  if (window.File && window.FileReader && window.FileList && window.Blob) {
    document.querySelector('form').addEventListener('submit', (e) => {
      e.preventDefault();
      const formData = new FormData(e.target);

      // replace original file
      const pointsFile = formData.get('points_file');
      truncatePointsFile(pointsFile, (truncatedFile) => {
        formData.set('points_file', truncatedFile, 'points.json');
        const xhr = new XMLHttpRequest();

        xhr.onreadystatechange = function () {
          if (xhr.readyState === 4) {
            if (xhr.status === 200) {
              window.location = xhr.responseURL;
            } else {
              alert(xhr.statusText);
            }
          }
        };

        xhr.open(e.target.method, e.target.action);
        xhr.send(formData);
      });
    });

    function truncatePointsFile(file, onSuccess, onError) {
      let reader = new FileReader();
      reader.readAsText(file);

      reader.onload = function () {
        const fromTimestamp = Date.now() - MAX_DAYS * 24 * 60 * 60 * 1000;

        let locations = JSON.parse(reader.result)['locations'];
        locations = locations.filter((visitedPoint) => {
          return parseInt(visitedPoint.timestampMs) >= fromTimestamp;
        });

        onSuccess(new Blob(
            [JSON.stringify({'locations': locations})],
            {type: "application/json"}
        ));
      };

      reader.onerror = function () {
        onError(reader.error);
      };
    }
  }
});
