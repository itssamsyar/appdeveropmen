const cards = document.querySelectorAll(".card")

let hasFlippedCard = false;
let lockboard = false;
let card; 
let generate = 0;

function flipCard() {
    if (lockboard) return;
    this.classList.add('flip');

    if (!hasFlippedCard) {
        var today = new Date();
        //first click
        hasFlippedCard = true;
        card = this;
        this.classList.add('chosen')
        lockboard = true;
        if (lockboard == true) {
            if ((this.classList.contains("chosen")) && (this.getAttribute('id') == 1)) {
                date = today.toLocaleDateString();
                time = today.toLocaleTimeString();
                generate = 1
                game = 2
            } else {
                generate = 0
            }
            transfer()
            setInterval(unflipCards, 1000);
        }
    } else {
        hasFlippedCard = false;
    }
}

(function shuffle() {
    cards.forEach(card => {
        let randomPos = Math.floor(Math.random() * 3);
        card.style.order = randomPos;
    });
})();

function unflipCards() {
    cards.forEach(card => card.classList.add('flip'))
}

cards.forEach(card => card.addEventListener("click", flipCard));


function transfer() {
    const dict_values = {generate, game, date, time}
    const s = JSON.stringify(dict_values)
    $.ajax({
        url:"/jspython",
        type:"POST",
        contentType:"application/json",
        data: JSON.stringify(s)});
}