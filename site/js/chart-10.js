/**
 * Chart 10 — B-HEARD coverage map.
 *
 * Choropleth of NYC police precincts shaded by 2024 felony-assault count
 * (Oranges ramp). The 31 B-HEARD precincts get an extra navy outline to mark
 * coverage. Below the SVG: a small HTML stats block with covered vs. not-
 * covered means, and a horizontal color legend.
 */
(function () {
  "use strict";
  const figure = document.getElementById("chart-10-container");
  if (!figure) return;
  const T = window.NYCStrategyChart;
  if (!T) return;

  function fmtNum(n) {
    if (n == null || isNaN(n)) return "—";
    return Number(n).toLocaleString(undefined, { maximumFractionDigits: 0 });
  }

  T.mountChart(figure, async function ({ width, Plot }) {
    const [geoResp, dataResp] = await Promise.all([
      fetch("data/precincts.geojson"),
      fetch("data/chart-10.json"),
    ]);
    if (!geoResp.ok || !dataResp.ok) throw new Error("Failed to fetch chart-10 data");
    const geojson = await geoResp.json();
    const data = await dataResp.json();

    // Index stats by integer precinct id and join onto geojson features.
    const statsByPct = new Map(
      data.stats.map(function (r) { return [parseInt(r.precinct, 10), r]; })
    );
    geojson.features.forEach(function (f) {
      const pct = parseInt(f.properties.precinct, 10);
      const s = statsByPct.get(pct);
      f.properties.count_2024 = s ? s.count_2024 : null;
      f.properties.bheard = !!(s && s.bheard);
    });

    // Domain: 0 → max count across precincts.
    const counts = data.stats
      .map(function (r) { return r.count_2024; })
      .filter(function (n) { return typeof n === "number" && !isNaN(n); });
    const maxCount = counts.length ? Math.max.apply(null, counts) : 1;

    // Subset of B-HEARD-covered features for the navy overlay.
    const bheardFeatures = {
      type: "FeatureCollection",
      features: geojson.features.filter(function (f) { return f.properties.bheard; }),
    };

    const colorScale = {
      type: "linear",
      scheme: "Oranges",
      domain: [0, maxCount],
      label: "Felony-assault count per precinct, 2024",
    };

    const svg = Plot.plot({
      width,
      height: 560,
      style: {
        background: "transparent",
        color: T.palette.ink,
        fontFamily: T.fonts.ui,
        fontSize: 13,
        overflow: "visible",
      },
      projection: { type: "mercator", domain: geojson },
      color: colorScale,
      marks: [
        Plot.geo(geojson, {
          fill: function (d) { return d.properties.count_2024; },
          stroke: "#fff",
          strokeWidth: 0.5,
          title: function (d) {
            const p = d.properties;
            return "Precinct " + p.precinct +
                   "\n2024 felony assaults: " + (p.count_2024 != null ? p.count_2024 : "?") +
                   (p.bheard ? "\nB-HEARD covered" : "");
          },
        }),
        // Navy overlay: B-HEARD-covered precincts only.
        Plot.geo(bheardFeatures, {
          fill: null,
          stroke: T.palette.navy,
          strokeWidth: 2.5,
        }),
      ],
    });

    // Color legend below the map.
    const legend = Plot.legend({ color: colorScale });
    legend.style.marginTop = "8px";

    // Stats block.
    const summary = data.summary || {};
    const stats = document.createElement("div");
    stats.className = "chart-10-stats";
    stats.innerHTML =
      "<strong>Felony-assault count, 2024 (mean per precinct):</strong><br>" +
      "&nbsp;&nbsp;B-HEARD-covered (" + fmtNum(summary.covered_count) + "): <strong>" + fmtNum(summary.covered_mean) + "</strong><br>" +
      "&nbsp;&nbsp;Not covered (" + fmtNum(summary.uncovered_count) + "): <strong>" + fmtNum(summary.uncovered_mean) + "</strong><br>" +
      "&nbsp;&nbsp;Ratio: <span class=\"ratio\">" +
        (summary.ratio != null ? Number(summary.ratio).toFixed(2) + "×" : "—") +
      "</span>";

    const outer = document.createElement("div");
    outer.className = "chart-10-render";
    outer.appendChild(svg);
    outer.appendChild(legend);
    outer.appendChild(stats);
    return outer;
  });
})();
