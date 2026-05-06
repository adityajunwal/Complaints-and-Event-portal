// Shared auth utilities used by all pages

const getToken  = () => localStorage.getItem("token");
const getName   = () => localStorage.getItem("userName");
const isAdmin   = () => localStorage.getItem("isAdmin") === "true";

const authHeaders = () => ({ "Authorization": `Bearer ${getToken()}` });

function checkAuth() {
  if (!getToken()) { window.location.href = "/static/index.html"; }
}

function logout() {
  localStorage.removeItem("token");
  localStorage.removeItem("userName");
  localStorage.removeItem("isAdmin");
  window.location.href = "/static/index.html";
}

function showAlert(id, msg, type = "error") {
  const el = document.getElementById(id);
  el.textContent = msg;
  el.className = `alert alert-${type} show`;
  setTimeout(() => el.classList.remove("show"), 4000);
}

function setNavUser() {
  const name = getName() || "User";
  const el = document.getElementById("nav-username");
  if (el) el.textContent = name;
  const mel = document.getElementById("mobile-username");
  if (mel) mel.textContent = name;
}

function toggleMenu() {
  const menu = document.getElementById("mobile-menu");
  const btn  = document.getElementById("hamburger-btn");
  const open = menu.classList.toggle("open");
  btn.textContent = open ? "✕" : "☰";
}
