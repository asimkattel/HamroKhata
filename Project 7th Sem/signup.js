function validateSignUp() {
    var email = document.getElementById("username").value;
    var password = document.getElementById("password").value;
    var cpassword = document.getElementById("confirmpassword").value;
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
    if (cpassword == "") {
      alert("Confirm Password field must be filled out");
      return false;
    }
    if (cpassword!==password) {
      alert("Password Does not Match");
      return false;
    }
    return true;
  }