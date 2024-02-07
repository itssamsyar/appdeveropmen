class Chatbox {
  // chatbot = Chatbox()
  constructor() {
    this.args = {
      openButton: document.querySelector(".chatbox__button"),
      chatBox: document.querySelector(".chatbox__support"),
      sendButton: document.querySelector(".send__button"),
    };

    this.state = false; // chatbot.state = false
    this.messages = []; // chatbot.messages = []
  }

  display() {
    const { openButton, chatBox, sendButton } = this.args;

    openButton.addEventListener("click", () => this.toggleState(chatBox)); // adds event listener to button element

    sendButton.addEventListener("click", () => this.onSendButton(chatBox));

    const inputs = chatBox.querySelector("input");
    inputs.addEventListener("keyup", ({ key }) => {
      if (key === "Enter") {
        this.onSendButton(chatBox);
      }
    });
  }

  toggleState(chatbox) {
    this.state = !this.state;

    if (this.state) {
      chatbox.classList.add("chatbox--active");
    } else {
      chatbox.classList.remove("chatbox--active");
    }
  }

  onSendButton(chatbox) {
    var textField = chatbox.querySelector("input");
    let text1 = textField.value;
    if (text1 === "") {
      return;
    }

    var username = document.getElementById("hiddenfield").value;
    let msg1 = { name: username, message: text1 };
    this.messages.push(msg1);

    fetch("/predict", {
      method: "POST",
      body: JSON.stringify({ user: username, message: text1}),
      headers: {
        "Content-Type": "application/json",
      },
    })
      .then((r) => r.json())
      .then((r) => {
        let msg2 = { name: "Solaris", message: r.reply };
        this.messages.push(msg2);
        this.updateChatText(chatbox);
        textField.value = " ";
      });
  }
  updateChatText(chatbox) {
    console.log("Received messages:", this.messages);

    var html = "";
    this.messages.slice().forEach(function (item) {
      if (item.name === "Solaris") {
        html +=
          '<div class="messages__item messages__item--visitor"><p>' +
          item.message +
          "</p></div>";
      } else {
        html +=
          '<div class="messages__item messages__item--operator"><p>' +
          item.message +
          "</p></div>";
      }
    });

    const chatmessage = chatbox.querySelector(".chatbox__messagesv2");
    chatmessage.innerHTML = html;
  }
}

const chatbox = new Chatbox();
chatbox.display();
