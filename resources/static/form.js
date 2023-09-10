const form = document.querySelector("form");
const sendButton = document.querySelector("button");
const statusLabel = document.getElementById("status");

sendButton.onclick = async function() {
    const data = Object.fromEntries((new FormData(form)).entries());

    await fetch(
        window.location + "/submit_answer",
        {
            method: "POST",
            headers: {
                "Accept": "application/json",
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        }
    )

    statusLabel.style.visibility = "visible";

    return false;
}
