const form = document.querySelector("form");
const sendButton = document.querySelector("button");

sendButton.onclick = async function() {
    const data = Object.fromEntries((new FormData(form)).entries());

    const responseJson = JSON.parse(
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
        ).then(response => response.text())
    );

    window.location += `/submissions/${responseJson["submission_id"]}`;

    return false;
}
