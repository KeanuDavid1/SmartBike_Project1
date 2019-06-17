
const postValuesInput = function() {
  password = document.querySelector('#password');
  Email = document.querySelector('#email');
  document.querySelector('#aanmelden').addEventListener('click', function() {
    if (password.value == '' || Email.value == '') {
      console.log('Fout message');
      if (document.querySelector('.c-status-message').innerHTML != null) {
        document.querySelector('.c-status-message').innerHTML = '';
      }
      innerHTMLElement = `
      <p><b>Fout:</b> Je vulde niet alle gegevens in.</p>`;
      document.querySelector('.c-status-message').innerHTML += innerHTMLElement;
      setTimeout(clearStatusMessage, 5000);
    } else {
      const body = {
        Password: password.value,
        Email: Email.value
      };

      handleData(
        `http://${IP}/api/smartbike/user/login`,
        verwerkResponse,
        'POST',
        JSON.stringify(body)
      );
    }
  });
};

const verwerkResponse = function(jsonObject) {
  if (jsonObject.message == 'E-mailadres of wachtwoord verkeerd') {
    if (document.querySelector('.c-status-message').innerHTML != null) {
      document.querySelector('.c-status-message').innerHTML = '';
    }
    innerHTMLElement = `<p>${jsonObject.message}</p>`;
    document.querySelector('#status-message').innerHTML += innerHTMLElement;
    setTimeout(clearStatusMessage, 5000);
  } else {
    window.location.replace(`http://${IPnoPort}/data.html`);
  }
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
};

document.addEventListener('DOMContentLoaded', function() {
  console.info('DOM geladen');
  init();
});
