let wheel = document.querySelector('.wheel')
let spinBtn = document.querySelector('.spinBtn')
let value = Math.ceil(Math.random() * 3000);
let lockboard = false;
const choice = document.getElementById("choice")
let hit = ""


        //create click event button spin
        spinBtn.onclick = function(){
            var today = new Date();


            if (lockboard) return;
            if (value <= 720) {
                value += 1080
            }
            let valuetemp = value;
            valuetemp -= 22.5
            wheel.style.transform = "rotate("+ valuetemp + "deg)";
            lockboard = true;


            //setInterval(display, 5000)
            setTimeout(display, 5000);
            date = today.toLocaleDateString();
            time = today.toLocaleTimeString();
            land();
            setTimeout(transfer, 5000);
        }

        function land() {
            a = 0
            while (value >= 360) {
                value -= 360
            }
            if (value < 45) {
                hit = "Nothing"
                a = 0
            } else if (value < 90) {
                hit = "Nothing"
                a = 0
            } else if (value < 135) {
                hit = "Nothing"
                a = 0
            } else if (value < 180) {
                hit = "Free delivery"
                a = 100
            } else if (value < 225) {
                hit = "Nothing"
                a = 0
            } else if (value < 270) {
                hit = "$10 off"
                a = 10
            } else if (value < 315) {
                hit = "Nothing"
                a = 0
            } else if (value < 360) {
                hit = "$1 off"
                a = 1
            }
        }

        function display() {
            choice.textContent = "You got " + hit
        }

        function transfer() {
            generate = a
            game = 1

            const dict_values = {generate, game, date, time}
            const s = JSON.stringify(dict_values)
            $.ajax({
                url:"/jspython",
                type:"POST",
                contentType:"application/json",
                data: JSON.stringify(s)});
        }