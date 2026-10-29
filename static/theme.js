document.getElementById("theme-toggle").addEventListener("click", function () {
  var root = document.documentElement;
  var dark = root.dataset.theme
    ? root.dataset.theme === "dark"
    : window.matchMedia("(prefers-color-scheme: dark)").matches;
  var next = dark ? "light" : "dark";
  root.dataset.theme = next;
  localStorage.setItem("theme", next);
});
