function toggleChatbot() {
    const bot = document.getElementById("chatbot");
    bot.style.display = bot.style.display === "block" ? "none" : "block";
}

function sendMessage() {
    const input = document.getElementById("chatInput");
    const body = document.getElementById("chatBody");

    if (input.value.trim() === "") return;

    body.innerHTML += `<p><strong>You:</strong> ${input.value}</p>`;
    body.innerHTML += `<p><strong>Bot:</strong> Thank you. We will assist you shortly.</p>`;

    input.value = "";
    body.scrollTop = body.scrollHeight;
}
