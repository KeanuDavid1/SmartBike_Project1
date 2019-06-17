'use strict';

const dataTimeImplementeren = function(arr01, arr02) {
  var ctx = document.getElementById('myChart').getContext('2d');
  var myChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: arr01,
      datasets: [
        {
          label: 'Time',
          data: arr02,
          backgroundColor: ['rgba(95, 124, 179, 0)'],
          borderColor: ['rgba(0, 0, 0, 1)'],
          borderWidth: 1,
        }
      ]
    },
    options: {
      scales: {
        yAxes: [
          {
            ticks: {
              beginAtZero: true
            }
          }
        ]
      }
    }
  });
};

const dataImplementeren = function(arr01, arr02) {
  var ctx = document.getElementById('myChart').getContext('2d');
  var myChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: arr01,
      datasets: [
        {
          label: 'Speed',
          data: arr02,
          backgroundColor: ['rgba(255, 99, 132, 0)'],
          borderColor: ['rgba(0, 0, 0, 1)'],
          borderWidth: 2,
          pointBackgroundColor: 'rgba(255,255,255,1)',
          pointBorderWidth: '1',
          pointRadius: '2'
        }
      ]
    },
    options: {
      scales: {
        yAxes: [
          {
            ticks: {
              beginAtZero: true
            }
          }
        ]
      }
    }
  });
};

// show Region________________________

const checkUser = function() {
  console.log('Checking user...');
  handleData(`http://${IP}/api/smartbike/user/check`, showCurrentUser, 'GET');
};

const showCurrentUser = function(jsonObject) {
  if (jsonObject.message == 'User niet ingelogd') {
    window.location.replace(`http://${IPnoPort}/index.html`);
  } else {
    console.log(jsonObject);
    for (let item of jsonObject) {
      document.querySelector(
        '#current-user'
      ).innerHTML = `<p>Ingelogd als: <b>${item.FirstName}</b> <b>${
        item.Name
      }</b></p>`;
    }
  }
};

const verwerkDataSpeed = function(jsonObject) {
  const arrSpeed = [];
  const arrDate = [];
  for (let item of jsonObject) {
    arrSpeed.push(item.Values);
    arrDate.push(item.Date.split(' ')[1] + ' ' + item.Date.split(' ')[2]);
  }
  dataImplementeren(arrDate, arrSpeed);
};

const verwerkDataTime = function(jsonObject) {
  const arrTime = [];
  const arrDate = [];
  for (let item of jsonObject) {
    arrTime.push(item[1]);
    arrDate.push(item[0]);
  }
  dataTimeImplementeren(arrDate, arrTime)
};

const showCurrentLocation = function(jsonObject) {
  const arrCO = [];
  for (let item of jsonObject) {
    arrCO.push(item.Values);
  }
  document.querySelector('.c-graph-data').innerHTML = '';
    const innerHTMLElement = `<div class="mapouter">
    <div class="gmap_canvas">
    <iframe width="100%" height="100%" id="gmap_canvas" src="https://maps.google.com/maps?q=${Math.max(
      arrCO[0],
      arrCO[1]
    )}%20${Math.min(
    arrCO[0],
    arrCO[1]
  )}&t=&z=13&ie=UTF8&iwloc=&output=embed" frameborder="0" scrolling="no" marginheight="0" marginwidth="0">
    </iframe>Google Maps Generator by <a href="https://www.embedgooglemap.net">embedgooglemap.net</a>
    </div>
    <style>.mapouter{position:relative;text-align:right;height:100%;width:100%;margin-left:auto;margin-right:auto;}.gmap_canvas {overflow:hidden;background:none!important;height:100%;width:100%;}
    </style></div>
    `;
  document.querySelector('.c-graph-data').innerHTML += innerHTMLElement;
};

const showAvgSpeed = function(jsonObject) {
  console.log(jsonObject);
  for (let item of jsonObject) {
    document.querySelector('#avgspeed').innerHTML = Math.round(item.avg);
  }
};

const showMaxSpeed = function(jsonObject) {
  console.log(jsonObject);
  for (let item of jsonObject) {
    document.querySelector('#topspeed').innerHTML = Math.round(item.max);
  }
};

const showExtraInfo = function() {
  console.log('Extra');
  document.querySelector('#avgspeed').innerHTML = '';
  // document.querySelector('#totaltime').innerHTML = "";
  document.querySelector('#topspeed').innerHTML = '';
  handleData(
    `http://${IP}/api/smartbike/user/extra-info-avgspeed`,
    showAvgSpeed,
    'GET'
  );
  handleData(
    `http://${IP}/api/smartbike/user/extra-info-maxspeed`,
    showMaxSpeed,
    'GET'
  );
};

const RedirectUser = function() {
  window.location.replace(`http://${IPnoPort}/index.html`);
};

// END show Region________________________

// listenTo___________________

const listenToLogout = function() {
  const button = document.querySelector('#logout-button');
  button.addEventListener('click', function() {
    console.log('Logout');
    handleData(`http://${IP}/api/smartbike/user/logout`, RedirectUser, 'POST');
  });
};

const listenToClickGPS = function() {
  document.querySelector('#gps').addEventListener('click', function() {
    handleData(
      `http://${IP}/api/smartbike/user/graph-data-gps`,
      showCurrentLocation,
      'GET'
    );
  });
};

const listenToClickTime = function() {
  document.querySelector('#time').addEventListener('click', function() {
    handleData(
      `http://${IP}/api/smartbike/user/graph-data-time`,
      verwerkDataTime,
      'GET'
    );
  });
};

const listenToClickSpeed = function() {
  document.querySelector('#speed').addEventListener('click', function() {
    document.querySelector('.c-graph-data').innerHTML = '';
    document.querySelector(
      '.c-graph-data'
    ).innerHTML += `<canvas id="myChart"></canvas>`;
    handleData(
      `http://${IP}/api/smartbike/user/graph-data-speed`,
      verwerkDataSpeed,
      'GET'
    );
  });
};

// END listenToRegion_________________

// INIT Region_________________

const init = function() {
  checkUser();
  showExtraInfo();
  handleData(
    `http://${IP}/api/smartbike/user/graph-data-speed`,
    verwerkDataSpeed,
    'GET'
  );
  listenToClickTime();
  listenToClickGPS();
  listenToClickSpeed();
  listenToLogout();
  // socketio
  buttonInfo();
};

document.addEventListener('DOMContentLoaded', function() {
  console.info('DOM geladen');
  init();
});
