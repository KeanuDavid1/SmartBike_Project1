const handleData = function(url, callback, method = 'GET', body = null) {
  fetch(url, {
    method: method,
    body: body,
    headers: { 'content-type': 'application/json' }
  })
    .then(function(response) {
      if (!response.ok) {
        throw Error(`Probleem bij de fetch(). Status Code: ${response.status}`);
      } else {
        console.info('Er is een response teruggekomen van de server');
        return response.json();
      }
    })
    .then(function(jsonObject) {
      console.info('json object is aangemaakt');
      console.info('verwerken data');
      callback(jsonObject);
    })
    .catch(function(error) {
      console.error(`fout bij verwerken json ${error}`);
    });
};
