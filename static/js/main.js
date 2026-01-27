/* ================= CHATBOT ================= */

function toggleChatbot() {
    const bot = document.getElementById("chatbot");
    bot.style.display = bot.style.display === "block" ? "none" : "block";
}

function sendMessage() {
    const input = document.getElementById("chatInput");
    const body = document.getElementById("chatBody");

    if (input.value.trim() === "") return;

    body.innerHTML += "<p><strong>You:</strong> " + input.value + "</p>";
    body.innerHTML += "<p><strong>Bot:</strong> Thank you. We will assist you shortly.</p>";

    input.value = "";
    body.scrollTop = body.scrollHeight;
}


/* ================= PAID MATERIAL EMAIL HANDLER ================= */

function copyEmail(id) {
    var emailInput = document.getElementById("email_" + id);
    var hiddenInput = document.getElementById("hidden_email_" + id);

    if (!emailInput || !hiddenInput) return;

    hiddenInput.value = emailInput.value;
}
/* ================= GMAIL VALIDATION ================= */

function validateGmail(id) {
    const emailInput = document.getElementById("email_" + id);
    const statusSpan = document.getElementById("email_status_" + id);
    const payBtn = document.getElementById("pay_btn_" + id);

    if (!emailInput || !statusSpan || !payBtn) return;

    const email = emailInput.value.trim();

    if (email.endsWith("@gmail.com")) {
        statusSpan.innerHTML = "✔️";
        statusSpan.style.color = "green";
        payBtn.disabled = false;
    } else {
        statusSpan.innerHTML = "❌";
        statusSpan.style.color = "red";
        payBtn.disabled = true;
    }
}

/* ================= MOBILE NAV ================= */
function toggleMobileNav() {
    const nav = document.getElementById("primaryNav");
    if (!nav) return;
    nav.classList.toggle("is-open");
}

/* Close mobile nav on outside click / ESC */
document.addEventListener("click", function (e) {
    const nav = document.getElementById("primaryNav");
    const toggle = document.querySelector(".nav-toggle");
    if (!nav || !toggle) return;

    if (!nav.classList.contains("is-open")) return;
    const clickedInside = nav.contains(e.target) || toggle.contains(e.target);
    if (!clickedInside) nav.classList.remove("is-open");
});

document.addEventListener("keydown", function (e) {
    if (e.key !== "Escape") return;
    const nav = document.getElementById("primaryNav");
    if (nav) nav.classList.remove("is-open");
});

/* ================= MODALS ================= */
function openModal(id) {
    const el = document.getElementById(id);
    if (!el) return;
    el.style.display = "flex";
    document.body.style.overflow = "hidden";
}

function closeModal(id) {
    const el = document.getElementById(id);
    if (!el) return;
    el.style.display = "none";
    document.body.style.overflow = "";
}

document.addEventListener("click", function (e) {
    const backdrop = e.target && e.target.classList && e.target.classList.contains("modal-backdrop");
    if (!backdrop) return;
    closeModal(e.target.id);
});

document.addEventListener("keydown", function (e) {
    if (e.key !== "Escape") return;
    const openBackdrop = document.querySelector(".modal-backdrop[style*='display: flex']");
    if (openBackdrop && openBackdrop.id) closeModal(openBackdrop.id);
});

/* ================= PASSWORD TOGGLE ================= */
function togglePassword(inputId, btn) {
    const input = document.getElementById(inputId);
    if (!input) return;
    const isPassword = input.type === "password";
    input.type = isPassword ? "text" : "password";
    if (btn) btn.textContent = isPassword ? "🙈" : "👁";
}

