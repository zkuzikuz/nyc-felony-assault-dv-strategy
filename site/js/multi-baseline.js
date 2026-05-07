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
  const PLOT_CDN = "https://cdn.jsdelivr.net/npm/@observablehq/plot@0.6/dist/plot.umd.min.js";

  function loadScript(src) {
    return new Promise(function (resolve, reject) {
      if (window.Plot) { resolve(); return; }
      const s = document.createElement("script");
      s.src = src;
      s.onload = resolve;
      s.onerror = reject;
      document.head.appendChild(s);
    });
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

  function renderPanel(container, data) {
    const Plot = window.Plot;
    const plot = Plot.plot({
      width: container.clientWidth,
      height: 280,
      x: { label: null },
      y: { label: "Percent change", grid: true, domain: data.length > 1 ? null : [0, Math.max(10, data[0].value * 1.2)] },
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
          dy: function (d) { return d.value >= 0 ? -8 : 16; },
          fill: "#1a1a1a",
          fontWeight: 700,
        }),
      ],
    });
    container.innerHTML = "";
    container.appendChild(plot);
    var svg = container.querySelector("svg");
    if (svg) {
      svg.setAttribute("role", "img");
      svg.setAttribute("aria-label", "Multi-baseline bar chart: how NYC's felony-assault rise looks at different time scales versus national peers.");
    }
  }

  async function init() {
    const figure = document.getElementById(CONTAINER_ID);
    if (!figure) return;
    const figcaption = figure.querySelector("figcaption");
    const captionText = figcaption ? figcaption.outerHTML : "";

    try {
      await loadScript(PLOT_CDN);
      const resp = await fetch("data/baseline-data.json");
      if (!resp.ok) throw new Error("Failed to fetch baseline data");
      const data = await resp.json();

      figure.innerHTML = "";
      // Tab strip
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
      figure.appendChild(tabs);

      const titleEl = document.createElement("div");
      titleEl.className = "baseline-title";
      figure.appendChild(titleEl);

      const renderTarget = document.createElement("div");
      renderTarget.className = "baseline-plot";
      figure.appendChild(renderTarget);

      const noteEl = document.createElement("div");
      noteEl.className = "baseline-note";
      figure.appendChild(noteEl);

      if (captionText) figure.insertAdjacentHTML("beforeend", captionText);

      function activate(key) {
        buttons.forEach(function (b) {
          b.classList.toggle("active", b.dataset.key === key);
        });
        titleEl.textContent = panelTitle(key, data);
        renderPanel(renderTarget, panelData(key, data));
        noteEl.textContent = panelNote(key, data);
      }

      buttons.forEach(function (b) {
        b.addEventListener("click", function () { activate(b.dataset.key); });
      });
      activate("decade"); // default

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
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
