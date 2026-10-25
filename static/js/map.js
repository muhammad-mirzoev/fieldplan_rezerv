(function () {
    const el = document.getElementById("map");
    if (!el) return;
  
    const saveUrl = el.dataset.saveUrl;
    const csrf = document.querySelector('meta[name="csrf-token"]').content;
    const boundary = JSON.parse(document.getElementById("field-boundary").textContent);
    const badge = document.getElementById("area-badge");
    const toastEl = document.getElementById("map-toast");
    const style = { color: "#5be15b", weight: 3, fillOpacity: 0.15 };
  
    // ---------- Карта и слои ----------
    let lat = parseFloat(String(el.dataset.lat).replace(",", "."));
    let lon = parseFloat(String(el.dataset.lon).replace(",", "."));
    if (isNaN(lat) || isNaN(lon)) {
      console.error("Некорректные координаты поля:", el.dataset.lat, el.dataset.lon);
      lat = 42.87; lon = 74.59;   // Бишкек
    }
    const map = L.map(el).setView([lat, lon], boundary ? 15 : 14);
  
    const satellite = L.tileLayer(
      "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
      { maxZoom: 19, attribution: "Esri, Maxar, Earthstar Geographics" });
    const labels = L.tileLayer(
      "https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}",
      { maxZoom: 19 });
    const streets = L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png",
      { maxZoom: 19, attribution: "© OpenStreetMap" });
  
    satellite.addTo(map);
    labels.addTo(map);   // подписи сёл поверх снимка (как «Сокулук» на макете)
    L.control.layers({ "Спутник": satellite, "Схема": streets }).addTo(map);
    L.control.scale({ metric: true, imperial: false }).addTo(map);
  
    // ---------- Граница поля ----------
    const drawn = new L.FeatureGroup().addTo(map);
    if (boundary) {
      L.geoJSON(boundary, { style }).eachLayer((l) => drawn.addLayer(l));
      map.fitBounds(drawn.getBounds(), { padding: [30, 30] });
    }
  
    map.addControl(new L.Control.Draw({
      draw: {
        polygon: { allowIntersection: false, showArea: false, shapeOptions: style },
        polyline: false, rectangle: false, circle: false,
        marker: false, circlemarker: false,
      },
      edit: { featureGroup: drawn, remove: false },
    }));
  
    function toast(text) {
      toastEl.textContent = text;
      toastEl.classList.add("show");
      setTimeout(() => toastEl.classList.remove("show"), 2500);
    }
  
    async function save() {
      const layer = drawn.getLayers()[0];
      if (!layer) return;
      const ring = layer.getLatLngs()[0];
      const areaHa = L.GeometryUtil.geodesicArea(ring) / 10000;  // м² → га
      const center = layer.getBounds().getCenter();
      try {
        const resp = await fetch(saveUrl, {
          method: "POST",
          headers: { "Content-Type": "application/json", "X-CSRFToken": csrf },
          body: JSON.stringify({
            geometry: layer.toGeoJSON().geometry,
            area_ha: areaHa, lat: center.lat, lon: center.lng,
          }),
        });
        if (!resp.ok) throw new Error(resp.status);
        const data = await resp.json();
        badge.textContent = data.area_ha + " га";
        toast("Границы сохранены");
      } catch (err) {
        toast("Не удалось сохранить границы");
      }
    }
  
    // Новый полигон заменяет старый: у поля одна граница
    map.on(L.Draw.Event.CREATED, (e) => {
      drawn.clearLayers();
      drawn.addLayer(e.layer);
      save();
    });
    map.on(L.Draw.Event.EDITED, save);
  
    // ---------- Поиск места (Nominatim) ----------
    const form = document.getElementById("map-search");
    const results = document.getElementById("search-results");
  
    function addItem(text, onClick) {
      const li = document.createElement("li");
      li.textContent = text;           // textContent, не innerHTML: защита от XSS
      if (onClick) li.addEventListener("click", onClick);
      results.append(li);
    }
  
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const q = form.q.value.trim();
      if (!q) return;
      results.innerHTML = "";
      const params = new URLSearchParams({
        q, format: "jsonv2", limit: 5, countrycodes: "kg", "accept-language": "ru",
      });
      try {
        const resp = await fetch("https://nominatim.openstreetmap.org/search?" + params);
        const items = await resp.json();
        if (!items.length) return addItem("Ничего не найдено");
        items.forEach((it) => addItem(it.display_name, () => {
          map.flyTo([+it.lat, +it.lon], 16);
          results.innerHTML = "";
        }));
      } catch (err) {
        addItem("Поиск временно недоступен");
      }
    });
  
    map.on("click", () => (results.innerHTML = ""));
  })();