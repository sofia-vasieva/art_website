/* Lightbox.
   Without JS every card is a plain link to its painting page, which works
   fine. With JS, a card opens the painting large with its caption already
   there -- no second click to read anything. Arrows and left/right keys move
   between paintings. */
(function () {
  "use strict";

  var blob = document.getElementById("gallery-data");
  var cards = Array.prototype.slice.call(document.querySelectorAll(".card"));
  if (!blob || !cards.length) return;

  var items;
  try {
    items = JSON.parse(blob.textContent);
  } catch (err) {
    return;                       // leave the plain links working
  }
  if (items.length !== cards.length) return;

  var lb = document.createElement("div");
  lb.className = "lb";
  lb.setAttribute("role", "dialog");
  lb.setAttribute("aria-modal", "true");
  lb.setAttribute("aria-label", "Painting");
  lb.innerHTML =
    '<button class="lb-close" aria-label="Close">&times;</button>' +
    '<button class="lb-btn lb-prev" aria-label="Previous painting">&#8249;</button>' +
    '<button class="lb-btn lb-next" aria-label="Next painting">&#8250;</button>' +
    '<div class="lb-body">' +
      '<div class="lb-stage"><img alt=""></div>' +
      '<div class="lb-info">' +
        '<h2 class="lb-title"></h2>' +
        '<p class="lb-meta"></p>' +
        '<div class="lb-caption"></div>' +
        '<div class="lb-views"></div>' +
        '<p class="lb-count"></p>' +
      '</div>' +
    '</div>';
  document.body.appendChild(lb);

  var img = lb.querySelector(".lb-stage img");
  var elTitle = lb.querySelector(".lb-title");
  var elMeta = lb.querySelector(".lb-meta");
  var elCaption = lb.querySelector(".lb-caption");
  var elViews = lb.querySelector(".lb-views");
  var elCount = lb.querySelector(".lb-count");
  var info = lb.querySelector(".lb-info");
  var index = -1;
  var lastFocus = null;

  function showView(item, n) {
    img.src = item.views[n].src;
    img.alt = item.alt;
    Array.prototype.forEach.call(elViews.children, function (b, i) {
      b.setAttribute("aria-current", i === n ? "true" : "false");
    });
  }

  function show(i) {
    if (i < 0) i = items.length - 1;
    if (i >= items.length) i = 0;
    index = i;
    var item = items[i];

    elTitle.textContent = item.title;
    elMeta.textContent = item.meta;
    elMeta.style.display = item.meta ? "" : "none";

    elCaption.textContent = "";
    item.caption.forEach(function (para) {
      var p = document.createElement("p");
      p.textContent = para;
      elCaption.appendChild(p);
    });

    // alternate views of the same painting, if there are any
    elViews.textContent = "";
    if (item.views.length > 1) {
      item.views.forEach(function (v, n) {
        var b = document.createElement("button");
        b.type = "button";
        b.className = "lb-view";
        b.setAttribute("aria-label", "View " + (n + 1));
        b.style.backgroundImage = "url(" + v.src + ")";
        b.addEventListener("click", function () { showView(item, n); });
        elViews.appendChild(b);
      });
    }

    elCount.textContent = (i + 1) + " of " + items.length;
    showView(item, 0);
    info.scrollTop = 0;
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
    c.addEventListener("click", function (ev) {
      if (ev.metaKey || ev.ctrlKey || ev.shiftKey || ev.button !== 0) return;
      ev.preventDefault();
      open(i);
    });
  });

  lb.querySelector(".lb-close").addEventListener("click", close);
  lb.querySelector(".lb-prev").addEventListener("click", function () { show(index - 1); });
  lb.querySelector(".lb-next").addEventListener("click", function () { show(index + 1); });
  lb.addEventListener("click", function (ev) {
    if (ev.target === lb) close();
  });

  document.addEventListener("keydown", function (ev) {
    if (!lb.hasAttribute("open-state")) return;
    if (ev.key === "Escape") close();
    else if (ev.key === "ArrowLeft") show(index - 1);
    else if (ev.key === "ArrowRight") show(index + 1);
  });
})();
