

// show region___________________________________

const postValuesInput = function() {
  Fnaam = document.querySelector('#Fnaam');
  Vnaam = document.querySelector('#Vnaam');
  password = document.querySelector('#password');
  passwordHerhaal = document.querySelector('#passwordHerhaling');
  Email = document.querySelector('#email');
  document.querySelector('#aanpassen').addEventListener('click', function() {
    if (
      Fnaam.value == '' ||
      Vnaam.value == '' ||
      password.value == '' ||
      passwordHerhaal.value == '' ||
      Email.value == ''
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
          Email: Email.value
        };
        handleData(
          `http://${IP}/api/smartbike/user/update`,
          verwerkResponse,
          'PUT',
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

const checkUser = function(){
  console.log('Checking user...')
  handleData(`http://${IP}/api/smartbike/user/check`, showCurrentUser, 'GET')
}

const showCurrentUser = function(jsonObject){
  if (jsonObject.message == 'User niet ingelogd'){
    window.location.replace(`http://${IPnoPort}/index.html`)
  } else {
    console.log(jsonObject)
    for (let item of jsonObject){
      document.querySelector('#current-user').innerHTML = `<p>Ingelogd als: <b>${item.FirstName}</b> <b>${item.Name}</b></p>`
    }
  }
}

const verwerkResponse = function(jsonObject) {
  if (document.querySelector('.c-status-message').innerHTML != null) {
    document.querySelector('.c-status-message').innerHTML = '';
  }
  if (jsonObject.message == 'Je bent niet ingelogt'){
    innerHTMLElement = `<p>${jsonObject.message}</p>`;
    document.querySelector('#status-message').innerHTML += innerHTMLElement;
  setTimeout(clearStatusMessage, 5000);
  } else{
    innerHTMLElement = `<p>${jsonObject.message}</p>`;
  document.querySelector('#status-message').classList.add("c-status-message-success");
  document.querySelector('#status-message').classList.remove("c-status-message");
  document.querySelector('#status-message').innerHTML += innerHTMLElement;
  setTimeout(clearStatusMessage, 5000);
  }
  
};

const verwerkDataUser = function(jsonObject){
  Fnaam = document.querySelector('#Fnaam');
  Vnaam = document.querySelector('#Vnaam');
  password = document.querySelector('#password');
  passwordHerhaal = document.querySelector('#passwordHerhaling');
  Email = document.querySelector('#email');
  for (let item of jsonObject){
    Fnaam.value = item.Name
    Vnaam.value = item.FirstName
    Email.value = item.Email
  }
}

const getValuesUser = function() {
  handleData(`http://${IP}/api/smartbike/user`, verwerkDataUser, 'GET');
};


// END Show region_________________________________

// listen to region____________________________________

const listenToLogout = function(){
  const button = document.querySelector('#logout-button')
  button.addEventListener('click', function(){
    console.log('Logout')
    handleData(`http://${IP}/api/smartbike/user/logout`, RedirectUser, 'POST')
  })
}

// end listen to region___________________________________

// utitity region_____________________________________

const RedirectUser = function(){
  window.location.replace(`http://${IPnoPort}/index.html`)
}


const clearStatusMessage = function() {
  message = document.querySelector('#status-message');
  if (message.innerHTML != null) {
    message.innerHTML = '';
    message.classList.add('c-status-message')
    console.log("Message cleared")
  }
};

// init region____________________________

const init = function() {
  checkUser();
  getValuesUser();
  postValuesInput();
  listenToLogout();
};

document.addEventListener('DOMContentLoaded', function() {
  console.info('DOM geladen');
  init();
});
