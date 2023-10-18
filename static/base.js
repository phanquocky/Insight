
function login_user(event) {
  event.preventDefault();
  window.location.href = "/sign_up";
};
function logout_user(event) {
  event.preventDefault();
  localStorage.removeItem("metamask_id");
  window.location.href = "/logout";
};