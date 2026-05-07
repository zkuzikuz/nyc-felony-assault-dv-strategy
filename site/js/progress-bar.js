/**
 * Reading-progress bar + sticky-TOC active-section tracking.
 *
 * - Reading progress: width of .progress-bar tracks scroll position vs document height.
 * - Active TOC: IntersectionObserver watches each <section> in main; the most-visible
 *   section's TOC <li> gets .active.
 *
 * Pure vanilla JS, no dependencies. Runs after DOMContentLoaded (defer attribute on <script>).
 */
(function () {
  "use strict";

  // --- reading progress ---
  const progressBar = document.querySelector('.progress-bar');

  function updateProgress() {
    if (!progressBar) return;
    const scrollTop = window.scrollY || document.documentElement.scrollTop;
    const docHeight = document.documentElement.scrollHeight - window.innerHeight;
    const pct = docHeight > 0 ? Math.min(100, (scrollTop / docHeight) * 100) : 0;
    progressBar.style.width = pct + '%';
    progressBar.setAttribute('aria-valuenow', Math.round(pct));
  }

  // throttle scroll handler with requestAnimationFrame
  let scrollScheduled = false;
  window.addEventListener('scroll', function () {
    if (scrollScheduled) return;
    scrollScheduled = true;
    requestAnimationFrame(function () {
      updateProgress();
      scrollScheduled = false;
    });
  }, { passive: true });

  updateProgress(); // initial

  // --- active TOC section ---
  const tocItems = document.querySelectorAll('.toc li');
  const tocSections = Array.from(document.querySelectorAll('.body section[id]'));

  function tocItemForId(id) {
    return Array.from(tocItems).find(function (li) {
      const a = li.querySelector('a');
      return a && a.getAttribute('href') === '#' + id;
    });
  }

  if (tocSections.length && 'IntersectionObserver' in window) {
    const visibilityMap = new Map();

    const observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        visibilityMap.set(entry.target.id, entry.intersectionRatio);
      });
      // pick the section with the highest intersection ratio (or first if all 0)
      let bestId = null;
      let bestRatio = -1;
      visibilityMap.forEach(function (ratio, id) {
        if (ratio > bestRatio) {
          bestRatio = ratio;
          bestId = id;
        }
      });
      tocItems.forEach(function (li) { li.classList.remove('active'); });
      if (bestId && bestRatio > 0) {
        const item = tocItemForId(bestId);
        if (item) item.classList.add('active');
      }
    }, {
      rootMargin: '-80px 0px -40% 0px',
      threshold: [0, 0.1, 0.25, 0.5, 0.75, 1.0],
    });

    tocSections.forEach(function (s) { observer.observe(s); });
  }

  // --- smooth scroll on TOC click ---
  document.querySelectorAll('.toc a[href^="#"]').forEach(function (link) {
    link.addEventListener('click', function (e) {
      const target = document.querySelector(link.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });
})();
