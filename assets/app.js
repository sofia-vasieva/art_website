/* Progressive enhancement: without JS every card is a plain link to its
   painting page, which works fine. With JS, cards open a lightbox instead. */
(function () {
  "use strict";

  var cards = Array.prototype.slice.call(
    document.querySelectorAll(".card[data-display]"));
  if (!cards.length) return;

  var lb = document.createElement("div");
  lb.className = "lb";
  lb.setAttribute("role", "dialog");
  lb.setAttribute("aria-modal", "true");
  lb.innerHTML =
    '<button class="lb-close" aria-label="Close">&times;</button>' +
    '<button class="lb-btn lb-prev" aria-label="Previous">&#8249;</button>' +
    '<button class="lb-btn lb-next" aria-label="Next">&#8250;</button>' +
    '<div class="lb-stage"><img alt=""></div>' +
    '<div class="lb-bar"><span class="t"></span>' +
    '<a class="lb-more" href="#">Read more &rarr;</a></div>';
  document.body.appendChild(lb);

  var img = lb.querySelector("img");
  var titleEl = lb.querySelector(".t");
  var moreEl = lb.querySelector(".lb-more");
  var index = -1;
  var lastFocus = null;

  function show(i) {
    if (i < 0) i = cards.length - 1;
    if (i >= cards.length) i = 0;
    index = i;
    var c = cards[i];
    img.src = c.getAttribute("data-display");
    img.alt = c.getAttribute("data-alt") || "";
    titleEl.textContent = c.getAttribute("data-title") || "";
    moreEl.href = c.getAttribute("href");
  }

  function open(i) {
    lastFocus = document.activeElement;
    show(i);
    lb.setAttribute("open-state", "1");
    document.body.style.overflow = "hidden";
    lb.querySelector(".lb-close").focus();
  }

  function close() {
    lb.removeAttribute("open-state");
    document.body.style.overflow = "";
    img.removeAttribute("src");
    if (lastFocus) lastFocus.focus();
  }

  cards.forEach(function (c, i) {
    c.addEventListener("click", function (e) {
      if (e.metaKey || e.ctrlKey || e.shiftKey || e.button !== 0) return;
      e.preventDefault();
      open(i);
    });
  });

  lb.querySelector(".lb-close").addEventListener("click", close);
  lb.querySelector(".lb-prev").addEventListener("click", function () { show(index - 1); });
  lb.querySelector(".lb-next").addEventListener("click", function () { show(index + 1); });
  lb.addEventListener("click", function (e) {
    if (e.target === lb || e.target.parentNode === lb.querySelector(".lb-stage")) {
      if (e.target === lb) close();
    }
  });

  document.addEventListener("keydown", function (e) {
    if (!lb.hasAttribute("open-state")) return;
    if (e.key === "Escape") close();
    else if (e.key === "ArrowLeft") show(index - 1);
    else if (e.key === "ArrowRight") show(index + 1);
  });
})();
