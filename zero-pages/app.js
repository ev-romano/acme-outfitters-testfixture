(function () {
  var mount = document.getElementById("app");
  fetch("./storefront-data/home.json")
    .then(function (response) { return response.ok ? response.json() : null; })
    .then(function (data) {
      if (!data || !mount) { return; }
      mount.textContent = String(data.headline || "");
    })
    .catch(function () {});
})();
