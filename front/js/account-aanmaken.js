const postValuesInput = function() {
  Fnaam = document.querySelector('#Fnaam');
  Vnaam = document.querySelector('#Vnaam');
  password = document.querySelector('#password');
  passwordHerhaal = document.querySelector('#passwordHerhaling');
  Email = document.querySelector('#email');
  RFID = document.querySelector('#RFID');
  document.querySelector('#aanpassen').addEventListener('click', function() {
    if (
      Fnaam.value == '' ||
      Vnaam.value == '' ||
      password.value == '' ||
      passwordHerhaal.value == '' ||
      Email.value == '' ||
      RFID.value == ''
    ) {
      console.log('Fout message');
      if (document.querySelector('.c-status-message').innerHTML != null) {
        document.querySelector('.c-status-message').innerHTML = '';
      }
      innerHTMLElement = `
        <p><b>Fout:</b> Je vulde niet alle gegevens in.</p>`;
      document.querySelector('.c-status-message').innerHTML += innerHTMLElement;
      setTimeout(clearStatusMessage, 5000);
    } else {
      if (password.value == passwordHerhaal.value) {
        const body = {
          Fnaam: Fnaam.value,
          Vnaam: Vnaam.value,
          Password: password.value,
          Email: Email.value,
          RFID: RFID.value
        };
        handleData(
          `http://${IP}/api/smartbike/user/account-aanmaken`,
          verwerkResponse,
          'POST',
          JSON.stringify(body)
        );
      } else {
        if (document.querySelector('.c-status-message').innerHTML != null) {
          document.querySelector('.c-status-message').innerHTML = '';
        }
        innerHTMLElement = `
          <p><b>Fout:</b> De wachtwoorden komen niet overeen</p>`;
        document.querySelector(
          '.c-status-message'
        ).innerHTML += innerHTMLElement;
        setTimeout(clearStatusMessage, 5000);
      }
    }
  });
};

const getRFIDtag = function() {
  socket.on('RFID-tag', function(data) {
    document.querySelector('#RFID').value = '';
    document.querySelector('#RFID').value = data;
  });
};

const verwerkResponse = function(jsonObject) {
  if (document.querySelector('.c-status-message').innerHTML != null) {
    document.querySelector('.c-status-message').innerHTML = '';
  }
  if (jsonObject.message == 'User bestaat al') {
    innerHTMLElement = `<p><strong>Error: </strong>${jsonObject.message}</p>`;
    document.querySelector('#status-message').innerHTML += innerHTMLElement;
    setTimeout(clearStatusMessage, 10000);
  } else {
    innerHTMLElement = `<p><strong>${jsonObject.message}</strong></p>`;
    document
      .querySelector('#status-message')
      .classList.add('c-status-message-success');
    document
      .querySelector('#status-message')
      .classList.remove('c-status-message');
    document.querySelector('#status-message').innerHTML += innerHTMLElement;
    setTimeout(redirect, 2000);
  }
};

const redirect = function() {
  window.location.replace(`http://${IPnoPort}/data.html`);
};

const clearStatusMessage = function() {
  message = document.querySelector('#status-message');
  if (message.innerHTML != null) {
    message.innerHTML = '';
    message.classList.add('c-status-message');
    console.log('Message cleared');
  }
};

const init = function() {
  postValuesInput();
  getRFIDtag();
};

document.addEventListener('DOMContentLoaded', function() {
  console.info('DOM geladen');
  init();
});
