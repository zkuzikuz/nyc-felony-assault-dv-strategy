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

  function loadScript() {
    if (window.NYCStrategyChart && window.NYCStrategyChart.loadPlot) {
      return window.NYCStrategyChart.loadPlot();
    }
    return Promise.reject(new Error("chart-theme.js not loaded"));
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

  /**
   * Renders the choropleth and returns the Plot SVG element WITHOUT touching
   * any container. Accepts an explicit width so it can work off-DOM.
   * Returns null if Plot is unavailable or throws.
   */
  function renderPlotStandalone(geojson, width) {
    var Plot = window.Plot;
    if (!Plot) return null;
    try {
      var plot = Plot.plot({
        width: width || 700,
        height: 600,
        projection: {
          type: "mercator",
          domain: geojson,
        },
        color: {
          type: "linear",
          scheme: "Oranges",
          domain: [-50, 0, 100, 200],
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
      return plot;
    } catch (e) {
      return null;
    }
  }

  function setMapAriaLabel(container) {
    var svg = container.querySelector("svg");
    if (svg) {
      svg.setAttribute("role", "img");
      svg.setAttribute("aria-label", "NYC precinct map: percent change in felony assault from 2017 to 2024, broken down by police precinct.");
    }
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
      var f = features[idx];
      var p = f ? f.properties : {};
      path.style.cursor = "pointer";
      path.setAttribute("tabindex", "0");
      path.setAttribute("role", "button");
      path.setAttribute("aria-label", "Precinct " + p.precinct + ", " + p.pct_change + "% change");
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
      path.addEventListener("keydown", function (e) {
        if (e.key === "Enter" || e.key === " ") {
          if (e.key === " ") e.preventDefault();
          e.stopPropagation();
          if (pinnedIdx === idx) {
            unpin();
            return;
          }
          paths.forEach(function (p) { p.classList.remove("pinned"); });
          path.classList.add("pinned");
          pinnedIdx = idx;
          var rect = container.getBoundingClientRect();
          var pathRect = path.getBoundingClientRect();
          showPinned(idx, pathRect.left - rect.left + 10, pathRect.top - rect.top + 10);
        }
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
    var figureWidth = figure.clientWidth || 720;

    try {
      await loadScript();
      if (!window.Plot) throw new Error("Observable Plot did not load");
      var geojson = await loadData();

      // Build the plot in a detached div first — no DOM changes yet
      var renderTarget = document.createElement("div");
      renderTarget.className = "chart-06-render";

      // Render off-DOM by passing width explicitly
      var plot = renderPlotStandalone(geojson, figureWidth);
      if (!plot) throw new Error("Plot.plot returned no element");
      renderTarget.appendChild(plot);

      var legendEl = window.Plot.legend({
        color: {
          type: "linear",
          scheme: "Oranges",
          domain: [-50, 0, 100, 200],
          label: "Percent change in felony assault, 2017 to 2024",
        },
      });
      legendEl.style.marginTop = "8px";
      renderTarget.appendChild(legendEl);

      setMapAriaLabel(renderTarget);
      attachPinHandlers(renderTarget, geojson);

      // Preserve figcaption
      var originalCaption = figure.querySelector("figcaption");
      var captionClone = originalCaption ? originalCaption.cloneNode(true) : null;

      // Success — atomically replace
      figure.innerHTML = "";
      figure.appendChild(renderTarget);
      if (captionClone) figure.appendChild(captionClone);

      // Re-render on resize (debounced).
      var resizeTimer;
      window.addEventListener("resize", function () {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(function () {
          var newPlot = renderPlotStandalone(geojson, renderTarget.clientWidth || figureWidth);
          if (newPlot) {
            renderTarget.innerHTML = "";
            renderTarget.appendChild(newPlot);
            // re-add legend
            var newLegend = window.Plot.legend({
              color: {
                type: "linear",
                scheme: "Oranges",
                domain: [-50, 0, 100, 200],
                label: "Percent change in felony assault, 2017 to 2024",
              },
            });
            newLegend.style.marginTop = "8px";
            renderTarget.appendChild(newLegend);
            setMapAriaLabel(renderTarget);
            attachPinHandlers(renderTarget, geojson);
          }
        }, 200);
      });
    } catch (err) {
      console.warn("Chart 06 interactive render failed; static PNG fallback in use.", err);
      figure.dataset.renderError = err.message || String(err);
      // Original innerHTML untouched; PNG fallback visible
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
