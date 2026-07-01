console.log("🔥 DISPLAY JS RAN");
async function loadScreen() {
    const token = window.screen_token;

    const res = await fetch(`/display/api/${token}`);
    const data = await res.json();

    const root = document.getElementById("sb_root");

    root.innerHTML = `
        <h1>${data.display.name}</h1>
        <p><b>Model:</b> ${data.display.model}</p>
        <p><b>ID:</b> ${data.record.id}</p>
        <p><b>Name:</b> ${data.record.name}</p>
    `;
}

document.addEventListener("DOMContentLoaded", loadScreen);