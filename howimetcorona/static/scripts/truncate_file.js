document.addEventListener("DOMContentLoaded", function() {
  const MAX_DAYS = 14;

  /*
  If FileReader API is supported we read the file content, truncate it to only
  include MAX_DAYS of data, put the results into a hidden field and remove the
  original file field so the file doesn't get uploaded.

  If not the view can also work with just the data.
  */
  if (window.File && window.FileReader && window.FileList && window.Blob) {
    document.querySelector('form').addEventListener('submit', (e) => {
      e.preventDefault();

      const form = e.target;
      const formData = new FormData(e.target);

      const pointsFile = formData.get('points_file');
      truncatePointsFile(pointsFile, (truncatedFileData) => {
        form.querySelector('[name=points_data]').value = truncatedFileData;
        // prevent file upload
        form.querySelector('[name=points_file]').value = '';
        form.submit();
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

        onSuccess(JSON.stringify({'locations': locations}));
      };

      reader.onerror = function () {
        onError(reader.error);
      };
    }
  }
});
