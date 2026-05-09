/**
 * Interactive multi-baseline view (chart 14).
 *
 * - Loads Observable Plot from CDN.
 * - Reads data/baseline-data.json.
 * - Renders a four-tab UI (1-year, 5-year, decade, national).
 * - Each tab swaps the rendered bar chart.
 * - If anything fails, the static PNG fallback already in the DOM stays.
 */
(function () {
  "use strict";

  const CONTAINER_ID = "chart-14-container";

  // Delegate to the shared loader so d3 + Plot load in the right order with a
  // single dedupe'd promise across all chart modules.
  function loadScript() {
    if (window.NYCStrategyChart && window.NYCStrategyChart.loadPlot) {
      return window.NYCStrategyChart.loadPlot();
    }
    return Promise.reject(new Error("chart-theme.js not loaded"));
  }

  function panelData(key, all) {
    if (key === "one_year") return [{ label: "NYC", value: all.one_year.value, fill: "#FF6319" }];
    if (key === "five_year") return [{ label: "NYC", value: all.five_year.value, fill: "#FF6319" }];
    if (key === "decade") return [
      { label: "Headline", value: all.decade.headline, fill: "#888" },
      { label: "Adjusted", value: all.decade.adjusted, fill: "#FF6319" },
    ];
    if (key === "national") return [
      { label: "NYC (adjusted)", value: all.national.nyc_adjusted, fill: "#D8127B" },
      { label: "US national", value: all.national.us_national, fill: "#888" },
      { label: "24-city avg", value: all.national.ccj_24_city, fill: "#888" },
      { label: "LA (2024 YoY)", value: all.national.la_yoy, fill: "#888" },
    ];
    return [];
  }

  function panelTitle(key, all) {
    return all[key].label;
  }

  function panelNote(key, all) { return all[key].note; }

  /**
   * Renders the bar chart and returns the SVG element WITHOUT touching any
   * container. Accepts an explicit width so it can work off-DOM.
   * Returns null if Plot is unavailable or throws.
   */
  function renderPanelStandalone(data, width) {
    var Plot = window.Plot;
    if (!Plot) return null;
    try {
      var plot = Plot.plot({
        width: width || 720,
        height: 280,
        x: { label: null },
        y: {
          label: "Percent change",
          grid: true,
          domain: data.length > 1 ? null : [0, Math.max(10, data[0].value * 1.2)],
        },
        marks: [
          Plot.barY(data, {
            x: "label",
            y: "value",
            fill: "fill",
            title: function (d) { return d.label + ": " + d.value + "%"; },
          }),
          Plot.ruleY([0]),
          Plot.text(data, {
            x: "label",
            y: "value",
            text: function (d) { return (d.value > 0 ? "+" : "") + d.value + "%"; },
            dy: -8,
            fill: "#1a1a1a",
            fontWeight: 700,
          }),
        ],
      });
      return plot;
    } catch (e) {
      console.warn("Chart 14 panel render error:", e);
      return null;
    }
  }

  function setSvgAriaLabel(container) {
    var svg = container.querySelector("svg");
    if (svg) {
      svg.setAttribute("role", "img");
      svg.setAttribute("aria-label", "Multi-baseline bar chart: NYC's felony-assault rise at different time scales versus national peers.");
    }
  }

  async function init() {
    const figure = document.getElementById(CONTAINER_ID);
    if (!figure) return;
    const figureWidth = figure.clientWidth || 720;

    try {
      await loadScript();
      if (!window.Plot) throw new Error("Plot did not load");
      const resp = await fetch("data/baseline-data.json");
      if (!resp.ok) throw new Error("Failed to fetch baseline data");
      const data = await resp.json();

      // Build the entire dynamic UI in a document fragment first
      const wrapper = document.createDocumentFragment();

      const tabs = document.createElement("div");
      tabs.className = "baseline-tabs";
      const panels = [
        { key: "one_year", label: "1-year" },
        { key: "five_year", label: "5-year" },
        { key: "decade", label: "Decade" },
        { key: "national", label: "National context" },
      ];
      const buttons = panels.map(function (p) {
        const b = document.createElement("button");
        b.type = "button";
        b.className = "baseline-tab";
        b.textContent = p.label;
        b.dataset.key = p.key;
        return b;
      });
      buttons.forEach(function (b) { tabs.appendChild(b); });
      wrapper.appendChild(tabs);

      const titleEl = document.createElement("div");
      titleEl.className = "baseline-title";
      wrapper.appendChild(titleEl);

      const renderTarget = document.createElement("div");
      renderTarget.className = "baseline-plot";
      wrapper.appendChild(renderTarget);

      const noteEl = document.createElement("div");
      noteEl.className = "baseline-note";
      wrapper.appendChild(noteEl);

      // Test-render to confirm Plot doesn't throw on the default tab BEFORE
      // we touch the figure. If Plot throws here, the catch block runs and
      // the original figure (with PNG fallback) is untouched.
      const testPlot = renderPanelStandalone(panelData("decade", data), figureWidth);
      if (!testPlot) throw new Error("Plot.plot returned no element for default tab");

      // Preserve the existing figcaption from the original figure
      const originalCaption = figure.querySelector("figcaption");
      const captionClone = originalCaption ? originalCaption.cloneNode(true) : null;

      // Success — atomically replace the figure's contents
      figure.innerHTML = "";
      figure.appendChild(wrapper);
      if (captionClone) figure.appendChild(captionClone);

      // Wire up state and activate default
      titleEl.textContent = panelTitle("decade", data);
      renderTarget.appendChild(testPlot);
      setSvgAriaLabel(renderTarget);
      noteEl.textContent = panelNote("decade", data);
      buttons.forEach(function (b) {
        if (b.dataset.key === "decade") b.classList.add("active");
      });

      function activate(key) {
        buttons.forEach(function (b) {
          b.classList.toggle("active", b.dataset.key === key);
        });
        titleEl.textContent = panelTitle(key, data);
        const newPlot = renderPanelStandalone(panelData(key, data), renderTarget.clientWidth || figureWidth);
        renderTarget.innerHTML = "";
        if (newPlot) renderTarget.appendChild(newPlot);
        setSvgAriaLabel(renderTarget);
        noteEl.textContent = panelNote(key, data);
      }

      buttons.forEach(function (b) {
        b.addEventListener("click", function () { activate(b.dataset.key); });
      });

      let resizeTimer;
      window.addEventListener("resize", function () {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(function () {
          const active = buttons.find(function (b) { return b.classList.contains("active"); });
          if (active) activate(active.dataset.key);
        }, 200);
      });
    } catch (err) {
      console.warn("Chart 14 interactive render failed; static PNG fallback in use.", err);
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
