/**
 * Shared theme + mount helper for Observable Plot charts.
 *
 * Exposes `window.NYCStrategyChart` with palette, font stacks, plot defaults,
 * and a `mountChart(figure, renderFn)` helper that:
 *   1. Lazy-loads Plot from the CDN,
 *   2. Calls `renderFn({ width, Plot })` to build an SVG,
 *   3. On success, replaces the figure body with the SVG (preserving the
 *      title block and figcaption),
 *   4. On any error, leaves the original PNG fallback intact and records the
 *      reason on `figure.dataset.renderError`.
 */
(function (global) {
  "use strict";

  const PLOT_CDN = "https://cdn.jsdelivr.net/npm/@observablehq/plot@0.6/dist/plot.umd.min.js";

  const palette = {
    orange: "#FF6319",
    magenta: "#D8127B",
    navy: "#003C71",
    ink: "#1a1a1a",
    paper: "#fafaf7",
    mute: "#888888",
    neutral: "#5a6473",
    light: "#e8e8e8",
    softLight: "#f0eee8",
  };

  const fonts = {
    body: "Newsreader, Georgia, 'Times New Roman', serif",
    ui: "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
  };

  function loadPlot() {
    return new Promise(function (resolve, reject) {
      if (global.Plot) { resolve(); return; }
      const s = document.createElement("script");
      s.src = PLOT_CDN;
      s.onload = resolve;
      s.onerror = function () { reject(new Error("Plot CDN load failed")); };
      document.head.appendChild(s);
    });
  }

  function _styleOneSvg(svg) {
    svg.style.background = "transparent";
    svg.style.fontFamily = fonts.ui;
    svg.style.color = palette.ink;
    svg.style.overflow = "visible";

    svg.querySelectorAll("[aria-label='x-axis'] path.domain, [aria-label='y-axis'] path.domain")
      .forEach(function (el) {
        el.setAttribute("stroke", palette.mute);
        el.setAttribute("stroke-opacity", "0.3");
      });
    svg.querySelectorAll("[aria-label='x-axis'] line, [aria-label='y-axis'] line")
      .forEach(function (el) {
        if (el.classList.contains("tick")) return;
        el.setAttribute("stroke-opacity", "0.15");
      });
    svg.querySelectorAll("[aria-label='x-grid'] line, [aria-label='y-grid'] line")
      .forEach(function (el) {
        el.setAttribute("stroke", palette.mute);
        el.setAttribute("stroke-opacity", "0.15");
        el.setAttribute("stroke-dasharray", "2 3");
      });
    svg.querySelectorAll("[aria-label='x-axis'] text, [aria-label='y-axis'] text, [aria-label='x-axis-label'], [aria-label='y-axis-label']")
      .forEach(function (el) {
        el.setAttribute("font-family", fonts.ui);
        el.setAttribute("fill", palette.neutral);
      });
  }

  // Apply editorial styling to one SVG, or to every SVG inside a container.
  function applyEditorialStyling(node) {
    if (!node) return;
    if (node.tagName && node.tagName.toLowerCase() === "svg") {
      _styleOneSvg(node);
      return;
    }
    if (node.querySelectorAll) {
      node.querySelectorAll("svg").forEach(_styleOneSvg);
    }
  }

  /**
   * Mount a chart inside a <figure>. Preserves any `.chart-title-block` and
   * `figcaption` already in the figure. On render error, leaves the PNG
   * fallback alone and tags `figure.dataset.renderError`.
   */
  async function mountChart(figure, renderFn) {
    if (!figure) return;
    const figureWidth = Math.max(280, figure.clientWidth || 720);
    try {
      await loadPlot();
      if (!global.Plot) throw new Error("Plot did not load");
      const node = await renderFn({ width: figureWidth, Plot: global.Plot });
      if (!node) throw new Error("renderFn returned no element");

      applyEditorialStyling(node);
      // role="img" is for SVGs; non-SVG containers may host their own labelling.
      if (node.tagName && node.tagName.toLowerCase() === "svg") {
        node.setAttribute("role", "img");
      }

      // Preserve the title block + figcaption from the original figure.
      const titleBlock = figure.querySelector(".chart-title-block");
      const figcaption = figure.querySelector("figcaption");
      const titleClone = titleBlock ? titleBlock.cloneNode(true) : null;
      const captionClone = figcaption ? figcaption.cloneNode(true) : null;

      figure.innerHTML = "";
      if (titleClone) figure.appendChild(titleClone);
      const wrap = document.createElement("div");
      wrap.className = "chart-render";
      wrap.appendChild(node);
      figure.appendChild(wrap);
      if (captionClone) figure.appendChild(captionClone);

      // Re-render on resize (debounced) — best-effort.
      let resizeTimer;
      global.addEventListener("resize", function () {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(async function () {
          try {
            const w = Math.max(280, figure.clientWidth || 720);
            const newNode = await renderFn({ width: w, Plot: global.Plot });
            if (!newNode) return;
            applyEditorialStyling(newNode);
            if (newNode.tagName && newNode.tagName.toLowerCase() === "svg") {
              newNode.setAttribute("role", "img");
            }
            wrap.innerHTML = "";
            wrap.appendChild(newNode);
          } catch (e) {
            // Silent — keep current rendering.
          }
        }, 200);
      });
    } catch (err) {
      console.warn("Chart render failed; PNG fallback in use.", err);
      figure.dataset.renderError = err.message || String(err);
    }
  }

  global.NYCStrategyChart = {
    palette,
    fonts,
    loadPlot,
    mountChart,
    applyEditorialStyling,
  };
})(window);
