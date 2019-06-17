const IP = window.location.host + ':5000';
const IPnoPort = window.location.host;
// const IP = '192.168.0.177' + ':5000';
// const IPnoPort = '192.168.0.177';
const socket = io.connect(IP);
socket.on('connect', function() {
  console.log(IP);
});

// toggle voor lichten via socketio

const buttonInfo = function() {
  const tekstVak = document.querySelector('#lichten');
  const checkBox = document.querySelector('#checkbox');
  console.log(checkBox);
  checkBox.addEventListener('change', function() {
    if (checkBox.checked) {
      console.log('change detected');
      socket.emit('change_status_led_on');
      socket.on('data', function(data) {
        tekstVak.innerHTML = data;
      });
    } else {
      socket.emit('change_status_led_off');
      console.log('change detected');
      socket.on('data', function(data) {
        tekstVak.innerHTML = data;
      });
    }
  });
};
