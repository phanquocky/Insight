
function login_user(event) {
  event.preventDefault();
  window.location.href = "/signup";
};
function logout_user(event) {
  event.preventDefault();
  localStorage.removeItem("metamask_id");
  window.location.href = "/logout";
};
