const button = document.querySelector("#buy_now_btn");
const price = document.getElementById("price").value;

const params = {
  price: price,
};
const options = {
  method: "POST",
  body: JSON.stringify(params),
};

button.addEventListener("click", (event) => {
  fetch("/stripe_pay", options)
    .then((result) => {
      return result.json();
    })
    .then((data) => {
      var stripe = Stripe(data.checkout_public_key);
      stripe.redirectToCheckout({
        sessionId: data.checkout_session_id,
      });
    });
});
