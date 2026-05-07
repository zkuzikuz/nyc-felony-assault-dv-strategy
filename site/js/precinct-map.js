/**
 * Interactive precinct map (chart 06).
 *
 * - Loads Observable Plot from CDN.
 * - Reads data/precincts.geojson and data/precinct-stats.json.
 * - Renders an orange-ramp choropleth of percent change in felony assault, 2017 to 2024.
 * - On hover: tooltip with precinct number, 2024 count, and percent change.
 * - On click: pin / unpin the tooltip.
 * - If anything fails, the static PNG fallback already in the DOM stays.
 */
(function () {
  "use strict";

  const CONTAINER_ID = "chart-06-container";
  const PLOT_CDN = "https://cdn.jsdelivr.net/npm/@observablehq/plot@0.6/dist/plot.umd.min.js";

  function loadScript(src) {
    return new Promise(function (resolve, reject) {
      const s = document.createElement("script");
      s.src = src;
      s.onload = resolve;
      s.onerror = reject;
      document.head.appendChild(s);
    });
  }

  async function loadData() {
    const [geoResp, statsResp] = await Promise.all([
      fetch("data/precincts.geojson"),
      fetch("data/precinct-stats.json"),
    ]);
    if (!geoResp.ok || !statsResp.ok) {
      throw new Error("Failed to fetch precinct data");
    }
    const geojson = await geoResp.json();
    const stats = await statsResp.json();
    // stats[i].precinct is an integer; geojson properties.precinct is a string.
    // parseInt ensures the Map lookup keys are always integers on both sides.
    const statsByPrecinct = new Map(stats.map(function (r) { return [parseInt(r.precinct, 10), r]; }));
    geojson.features.forEach(function (f) {
      const pct = parseInt(f.properties.precinct, 10);
      const stat = statsByPrecinct.get(pct);
      if (stat) {
        f.properties.count_2017 = stat.count_2017;
        f.properties.count_2024 = stat.count_2024;
        f.properties.pct_change = stat.pct_change;
      }
    });
    return geojson;
  }

  function renderPlot(container, geojson) {
    var Plot = window.Plot;
    if (!Plot) return;
    var plot = Plot.plot({
      width: container.clientWidth || 700,
      height: 600,
      projection: {
        type: "mercator",
        domain: geojson,
      },
      color: {
        type: "linear",
        scheme: "Oranges",
        domain: [-50, 0, 100, 200],
        legend: true,
        label: "Percent change in felony assault, 2017 to 2024",
      },
      marks: [
        Plot.geo(geojson, {
          fill: function (d) { return d.properties.pct_change; },
          stroke: "#fff",
          strokeWidth: 0.5,
          title: function (d) {
            var p = d.properties;
            return "Precinct " + p.precinct +
                   "\n2017: " + (p.count_2017 != null ? p.count_2017 : "?") +
                   "\n2024: " + (p.count_2024 != null ? p.count_2024 : "?") +
                   "\nChange: " + (p.pct_change != null ? p.pct_change + "%" : "?");
          },
        }),
      ],
    });
    container.innerHTML = "";
    container.appendChild(plot);
    attachPinHandlers(container, geojson);
  }

  // Click-to-pin: clicking a precinct pins a sticky tooltip with its info;
  // clicking the same precinct again unpins; clicking another swaps.
  function attachPinHandlers(container, geojson) {
    var features = geojson.features;
    var paths = container.querySelectorAll("svg path");
    if (!paths.length) return;

    var pinnedIdx = null;

    // Tooltip element (created once per render).
    var tip = document.createElement("div");
    tip.className = "precinct-pin-tip";
    tip.style.display = "none";
    container.appendChild(tip);

    function showPinned(idx, x, y) {
      var f = features[idx];
      if (!f) return;
      var p = f.properties;
      tip.innerHTML =
        "<strong>Precinct " + p.precinct + "</strong>" +
        "<div>2017: " + (p.count_2017 != null ? Number(p.count_2017).toLocaleString() : "—") + "</div>" +
        "<div>2024: " + (p.count_2024 != null ? Number(p.count_2024).toLocaleString() : "—") + "</div>" +
        "<div class='pct'>" + (p.pct_change != null ? (p.pct_change > 0 ? "+" : "") + p.pct_change + "%" : "—") + "</div>" +
        "<button class='unpin-btn' aria-label='Unpin precinct'>&times;</button>";
      tip.style.left = x + "px";
      tip.style.top = y + "px";
      tip.style.display = "block";
      var btn = tip.querySelector(".unpin-btn");
      if (btn) {
        btn.addEventListener("click", function (e) {
          e.stopPropagation();
          unpin();
        });
      }
    }

    function unpin() {
      pinnedIdx = null;
      tip.style.display = "none";
      paths.forEach(function (p) { p.classList.remove("pinned"); });
    }

    paths.forEach(function (path, idx) {
      path.style.cursor = "pointer";
      path.addEventListener("click", function (e) {
        e.stopPropagation();
        if (pinnedIdx === idx) {
          unpin();
          return;
        }
        paths.forEach(function (p) { p.classList.remove("pinned"); });
        path.classList.add("pinned");
        pinnedIdx = idx;
        var rect = container.getBoundingClientRect();
        showPinned(idx, e.clientX - rect.left + 10, e.clientY - rect.top + 10);
      });
    });

    // Click outside the map paths → unpin.
    container.addEventListener("click", function (e) {
      if (e.target === container || e.target === tip) unpin();
    });
  }

  async function init() {
    var figure = document.getElementById(CONTAINER_ID);
    if (!figure) return;
    var figcaption = figure.querySelector("figcaption");
    var captionText = figcaption ? figcaption.outerHTML : "";

    try {
      await loadScript(PLOT_CDN);
      if (!window.Plot) throw new Error("Observable Plot did not load");
      var geojson = await loadData();
      var renderTarget = document.createElement("div");
      renderTarget.className = "chart-06-render";
      figure.innerHTML = "";
      figure.appendChild(renderTarget);
      if (captionText) figure.insertAdjacentHTML("beforeend", captionText);
      renderPlot(renderTarget, geojson);
      // Re-render on resize (debounced).
      var resizeTimer;
      window.addEventListener("resize", function () {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(function () {
          renderPlot(renderTarget, geojson);
        }, 200);
      });
    } catch (err) {
      console.warn("Chart 06 interactive render failed; static PNG fallback in use.", err);
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
