document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("chat-form");
    const input = document.getElementById("chat-input");
    const chatContainer = document.getElementById("chat-container");

    if (!form || !input || !chatContainer) {
        console.error("Required elements not found in DOM");
        return;
    }

    form.addEventListener("submit", async function (e) {
        e.preventDefault();
        const msg = input.value.trim();
        if (!msg) return;

        // Append player message
        const playerMsg = document.createElement("div");
        playerMsg.textContent = "You: " + msg;
        chatContainer.appendChild(playerMsg);
        input.value = "";

        // Send message to server
        try {
            const resp = await fetch("/message", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: msg })
            });
            const data = await resp.json();

            // Format AI response nicely
            let dmText = "";
            if (data.error) {
                dmText = "Error: " + data.error;
            } else if (data.narration) {
                dmText = data.narration;
            } else {
                dmText = JSON.stringify(data);
            }

            const dmMsg = document.createElement("div");
            dmMsg.textContent = "DM: " + dmText;
            chatContainer.appendChild(dmMsg);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        } catch (err) {
            console.error("Error sending message:", err);
            const dmMsg = document.createElement("div");
            dmMsg.textContent = "DM: Failed to send message.";
            chatContainer.appendChild(dmMsg);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
    });
});
