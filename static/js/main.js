/* AroundU interactions: navigation, reveal, filters, copy, calendar, export. */
(function () {
    "use strict";

    var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    /* ---------- header + scroll progress ---------- */

    var header = document.getElementById("siteHeader");
    var progress = document.getElementById("scrollProgress");

    function onScroll() {
        var y = window.scrollY || document.documentElement.scrollTop;
        if (header) {
            header.classList.toggle("is-scrolled", y > 8);
        }
        if (progress) {
            var max = document.documentElement.scrollHeight - window.innerHeight;
            progress.style.width = (max > 0 ? (y / max) * 100 : 0) + "%";
        }
    }

    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();

    /* ---------- mobile navigation ---------- */

    var navToggle = document.getElementById("navToggle");
    var navMenu = document.getElementById("navMenu");

    function closeNav() {
        if (!navToggle || !navMenu) return;
        navToggle.setAttribute("aria-expanded", "false");
        navMenu.classList.remove("is-open");
        document.body.classList.remove("nav-open");
    }

    if (navToggle && navMenu) {
        navToggle.addEventListener("click", function () {
            var open = navToggle.getAttribute("aria-expanded") === "true";
            navToggle.setAttribute("aria-expanded", String(!open));
            navMenu.classList.toggle("is-open", !open);
            document.body.classList.toggle("nav-open", !open);
        });

        navMenu.querySelectorAll("a").forEach(function (link) {
            link.addEventListener("click", closeNav);
        });

        document.addEventListener("keydown", function (event) {
            if (event.key === "Escape") closeNav();
        });

        window.addEventListener("resize", function () {
            if (window.innerWidth > 960) closeNav();
        });
    }

    /* ---------- scroll reveal ---------- */

    var revealItems = document.querySelectorAll("[data-reveal]");
    if (revealItems.length && "IntersectionObserver" in window && !reduceMotion) {
        var revealObserver = new IntersectionObserver(
            function (entries) {
                entries.forEach(function (entry) {
                    if (entry.isIntersecting) {
                        entry.target.classList.add("is-visible");
                        revealObserver.unobserve(entry.target);
                    }
                });
            },
            { rootMargin: "0px 0px -8% 0px", threshold: 0.08 }
        );
        revealItems.forEach(function (item) {
            revealObserver.observe(item);
        });
    } else {
        revealItems.forEach(function (item) {
            item.classList.add("is-visible");
        });
    }

    /* ---------- animated counters ---------- */

    function animateCounter(el) {
        var target = parseInt(el.getAttribute("data-count"), 10);
        if (isNaN(target) || reduceMotion) return;
        var start = performance.now();
        var duration = 900;
        function frame(now) {
            var progressValue = Math.min((now - start) / duration, 1);
            var eased = 1 - Math.pow(1 - progressValue, 3);
            el.textContent = String(Math.round(target * eased));
            if (progressValue < 1) requestAnimationFrame(frame);
        }
        el.textContent = "0";
        requestAnimationFrame(frame);
    }

    var counters = document.querySelectorAll("[data-count]");
    if (counters.length && "IntersectionObserver" in window && !reduceMotion) {
        var counterObserver = new IntersectionObserver(
            function (entries) {
                entries.forEach(function (entry) {
                    if (entry.isIntersecting) {
                        animateCounter(entry.target);
                        counterObserver.unobserve(entry.target);
                    }
                });
            },
            { threshold: 0.4 }
        );
        counters.forEach(function (counter) {
            counterObserver.observe(counter);
        });
    }

    /* ---------- toasts ---------- */

    document.querySelectorAll(".toast").forEach(function (toast) {
        var timer;
        function dismiss() {
            toast.classList.add("is-hiding");
            window.setTimeout(function () {
                toast.remove();
            }, 320);
        }
        var close = toast.querySelector(".toast-close");
        if (close) close.addEventListener("click", dismiss);
        timer = window.setTimeout(dismiss, 6000);
        toast.addEventListener("mouseenter", function () {
            window.clearTimeout(timer);
        });
    });

    /* ---------- confirmation prompts ---------- */

    document.querySelectorAll("form[data-confirm]").forEach(function (form) {
        form.addEventListener("submit", function (event) {
            if (!window.confirm(form.getAttribute("data-confirm"))) {
                event.preventDefault();
            }
        });
    });

    /* ---------- filters ---------- */

    document.querySelectorAll("form[data-auto-submit] select").forEach(function (select) {
        select.addEventListener("change", function () {
            select.form.submit();
        });
    });

    var searchInput = document.getElementById("q");
    if (searchInput) {
        document.addEventListener("keydown", function (event) {
            var tag = (event.target.tagName || "").toLowerCase();
            var typing = tag === "input" || tag === "textarea" || tag === "select" || event.target.isContentEditable;
            if (event.key === "/" && !typing) {
                event.preventDefault();
                searchInput.focus();
                searchInput.select();
            }
        });
    }

    /* ---------- copy to clipboard ---------- */

    function copyText(text) {
        if (navigator.clipboard && window.isSecureContext) {
            return navigator.clipboard.writeText(text);
        }
        return new Promise(function (resolve, reject) {
            var field = document.createElement("textarea");
            field.value = text;
            field.style.position = "fixed";
            field.style.opacity = "0";
            document.body.appendChild(field);
            field.select();
            try {
                document.execCommand("copy");
                resolve();
            } catch (error) {
                reject(error);
            } finally {
                field.remove();
            }
        });
    }

    document.querySelectorAll("[data-copy]").forEach(function (button) {
        var original = button.innerHTML;
        button.addEventListener("click", function () {
            copyText(button.getAttribute("data-copy"))
                .then(function () {
                    button.innerHTML = original.replace(/Copy (link|event link)/i, "Copied");
                    window.setTimeout(function () {
                        button.innerHTML = original;
                    }, 1800);
                })
                .catch(function () {
                    window.prompt("Copy this link", button.getAttribute("data-copy"));
                });
        });
    });

    /* ---------- add to calendar ---------- */

    function icsDate(value) {
        return value.replace(/-/g, "");
    }

    function escapeIcs(value) {
        return String(value || "")
            .replace(/\\/g, "\\\\")
            .replace(/;/g, "\\;")
            .replace(/,/g, "\\,")
            .replace(/\n/g, "\\n");
    }

    document.querySelectorAll("[data-ics]").forEach(function (button) {
        button.addEventListener("click", function () {
            var start = button.getAttribute("data-ics-start") || "";
            var title = button.getAttribute("data-ics-title") || "AroundU event";
            var location = button.getAttribute("data-ics-location") || "";
            var description = button.getAttribute("data-ics-description") || "";
            var url = button.getAttribute("data-ics-url") || window.location.href;
            var stamp = new Date().toISOString().replace(/[-:]/g, "").split(".")[0] + "Z";

            var lines = [
                "BEGIN:VCALENDAR",
                "VERSION:2.0",
                "PRODID:-//AroundU//Events//EN",
                "CALSCALE:GREGORIAN",
                "BEGIN:VEVENT",
                "UID:" + stamp + "@aroundu",
                "DTSTAMP:" + stamp,
                "DTSTART;VALUE=DATE:" + icsDate(start),
                "DTEND;VALUE=DATE:" + icsDate(start),
                "SUMMARY:" + escapeIcs(title),
                "LOCATION:" + escapeIcs(location),
                "DESCRIPTION:" + escapeIcs(description + " " + url),
                "END:VEVENT",
                "END:VCALENDAR"
            ];

            var blob = new Blob([lines.join("\r\n")], { type: "text/calendar;charset=utf-8" });
            var link = document.createElement("a");
            link.href = URL.createObjectURL(blob);
            link.download = title.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "") + ".ics";
            document.body.appendChild(link);
            link.click();
            link.remove();
            URL.revokeObjectURL(link.href);
        });
    });

    /* ---------- application table filters ---------- */

    var statusTabs = document.querySelectorAll("[data-status-filter]");
    if (statusTabs.length) {
        var rows = document.querySelectorAll("#applicants tbody tr");
        var emptyRow = document.querySelector("[data-table-empty]");

        function applyStatusFilter(status) {
            var visible = 0;
            rows.forEach(function (row) {
                var match = status === "all" || row.getAttribute("data-status") === status;
                row.hidden = !match;
                if (match) visible += 1;
            });
            statusTabs.forEach(function (tab) {
                tab.classList.toggle("is-active", tab.getAttribute("data-status-filter") === status);
            });
            if (emptyRow) emptyRow.hidden = visible !== 0;
        }

        statusTabs.forEach(function (tab) {
            tab.addEventListener("click", function () {
                applyStatusFilter(tab.getAttribute("data-status-filter"));
            });
        });
    }

    /* ---------- CSV export ---------- */

    document.querySelectorAll("[data-export-csv]").forEach(function (button) {
        button.addEventListener("click", function () {
            var table = document.getElementById(button.getAttribute("data-export-csv"));
            if (!table) return;
            var rows = Array.prototype.slice.call(table.querySelectorAll("tbody tr"));
            var lines = [["Name", "Email", "College", "Applied", "Status"]];

            rows.forEach(function (row) {
                lines.push([
                    row.getAttribute("data-name") || "",
                    row.getAttribute("data-email") || "",
                    row.getAttribute("data-college") || "",
                    row.getAttribute("data-applied") || "",
                    row.getAttribute("data-status") || ""
                ]);
            });

            var csv = lines.map(function (line) {
                return line.map(function (cell) {
                    return '"' + String(cell).replace(/"/g, '""') + '"';
                }).join(",");
            }).join("\r\n");

            var blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
            var link = document.createElement("a");
            link.href = URL.createObjectURL(blob);
            link.download = "aroundu-applicants.csv";
            document.body.appendChild(link);
            link.click();
            link.remove();
            URL.revokeObjectURL(link.href);
        });
    });

    /* ---------- cover image preview ---------- */

    var imageInput = document.querySelector("[data-image-input]");
    var imagePreview = document.querySelector("[data-image-preview]");
    if (imageInput && imagePreview) {
        var previewImage = imagePreview.querySelector("img");
        function syncPreview() {
            var value = imageInput.value.trim();
            var valid = /^https?:\/\//i.test(value);
            imagePreview.hidden = !valid;
            if (valid && previewImage) previewImage.src = value;
        }
        imageInput.addEventListener("input", syncPreview);
        imageInput.addEventListener("blur", syncPreview);
    }

    /* ---------- "Other" college field ---------- */

    var collegeSelect = document.querySelector("[data-college-select]");
    var otherCollege = document.querySelector("[data-other-college]");
    if (collegeSelect && otherCollege) {
        var otherInput = otherCollege.querySelector("input");
        function syncOtherCollege(focus) {
            var isOther = collegeSelect.value === "Other";
            otherCollege.hidden = !isOther;
            if (otherInput) {
                otherInput.required = isOther;
                if (isOther && focus) otherInput.focus();
            }
        }
        collegeSelect.addEventListener("change", function () {
            syncOtherCollege(true);
        });
        syncOtherCollege(false);
    }
})();
