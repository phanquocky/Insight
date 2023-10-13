
function login_user(event) {
  event.preventDefault();
  window.location.href = "/signup";
};
function logout_user(event) {
  event.preventDefault();
  window.location.href = "/logout";
};

const connectMetamaskButton = document.getElementById("connect-metamask-btn");
if(localStorage.getItem('metamask_id')) {
    connectMetamaskButton.innerHTML = localStorage.getItem('metamask_id');
}