const guess = document.getElementById("guess");
const submit = document.getElementById("submit")
const hint = document.getElementById("hint")
const attemptText = document.getElementById("attempts")
let value = Math.ceil(Math.random() * 100 + 1);
let lockboard = false;
let attempts = 0;
var invalidChars = ["-", "+", "e", " "];
var today = new Date();
console.log(value)

guess.addEventListener("keydown", function(e) {
    if (invalidChars.includes(e.key)) {
        e.preventDefault();
    }
});

submit.addEventListener("click", check)

function check() {
    if (lockboard) return;
    const userValue = Number(guess.value);
    var x = document.getElementById("guess").value;
    if ((userValue < 0) || (userValue > 100) || (x == "")) {
        if (userValue < 0) {
            hint.textContent = "Invalid number. Please enter a positive number."
        } else if (userValue > 100) {
            hint.textContent = "Number out of range. Please enter a number between 0 and 100."
        } else {
            hint.textContent = "Please enter a number between 0 and 100."
        }
    } else {
        attempts += 1
        lockboard = true
        if (userValue === value) {
            generate = 1
            game = 4
            hint.textContent = "Congratulations, you got a discount coupon of $1 off."
            date = today.toLocaleDateString();
            time = today.toLocaleTimeString();
            transfer();
        } else if ((userValue < value) || (userValue > value)) {
            if (userValue < value) {
                hint.textContent = "Too low! Try again.";
            } else {
                hint.textContent = "Too high! Try again.";
            }

            if (attempts != 10) {
                lockboard = false
            } else {
                lockboard = true
                generate = 0
                hint.textContent = "The number was " + value
            }
        }
    }
    attemptText.textContent = "Attempts: " + attempts;
}

function transfer() {
    const dict_values = {generate, game, date, time}
    const s = JSON.stringify(dict_values)
    $.ajax({
        url:"/jspython",
        type:"POST",
        contentType:"application/json",
        data: JSON.stringify(s)});
}