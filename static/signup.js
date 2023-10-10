const loginText = document.querySelector(".title-text .login");
const loginForm = document.querySelector("form.login");
const loginBtn = document.querySelector("label.login");
const signupBtn = document.querySelector("label.signup");
const signupLink = document.querySelector("form .signup-link a");
signupBtn.onclick = (() => {
    loginForm.style.marginLeft = "-50%";
    loginText.style.marginLeft = "-50%";
});
loginBtn.onclick = (() => {
    loginForm.style.marginLeft = "0%";
    loginText.style.marginLeft = "0%";
});
signupLink.onclick = (() => {
    signupBtn.click();
    return false;
});

document.getElementById("generateButton").addEventListener("click", async(e) => {
    e.preventDefault();
    let username = document.getElementById('username');
    let password = document.getElementById('password');
    let confirm = document.getElementById('confirm');
    if (password.value != confirm.value) {
        alert("Passwords must match!");
        return;
    }
    if (password.value.length < 6) {
        alert("Passwords is at least 6 characters!");
        return;
    }

    let spinner = document.getElementById('spinner');
    let public = document.getElementById('public_key');
    let private = document.getElementById('private_key');

    spinner.classList.remove("d-none");
    await sleep(300);

    let response = await fetch(`/generateKey`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            "username" : username.value,
            "password": password.value
            }),
    }).then((res) => res.json());
   
    public.value = response["public_key"];
    private.value = response["private_key"];
    spinner.classList.add("d-none");
});

const sleep = ms => new Promise(r => setTimeout(r, ms));
