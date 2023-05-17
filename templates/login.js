function validateForm() {
    var email = document.getElementById("uname").value;
    var password = document.getElementById("pwd").value;
    var emailRegex = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$/;
    if (email == "") {
      alert("Email field must be filled out");
      return false;
    }
    if (!email.match(emailRegex)) {
      alert("Please enter a valid email address");
      return false;
    }
    if (password == "") {
      alert("Password field must be filled out");
      return false;
    }
    return true;
  }