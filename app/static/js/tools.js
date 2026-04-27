const navToggle = document.querySelector(".nav-toggle");
const navLinks = document.querySelector(".nav-links");
const themeToggle = document.querySelector(".theme-toggle");
const siteSearch = document.querySelector("#site-search");

const savedTheme = localStorage.getItem("isocentre-theme");
if (savedTheme === "dark" || (!savedTheme && window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches)) {
  document.documentElement.dataset.theme = "dark";
}

if (themeToggle) {
  themeToggle.addEventListener("click", () => {
    const nextTheme = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
    document.documentElement.dataset.theme = nextTheme;
    localStorage.setItem("isocentre-theme", nextTheme);
  });
}

if (navToggle && navLinks) {
  navToggle.addEventListener("click", () => {
    const isOpen = navLinks.classList.toggle("open");
    navToggle.setAttribute("aria-expanded", String(isOpen));
  });
}

document.addEventListener("keydown", (event) => {
  if (event.key === "/" && siteSearch && !["INPUT", "TEXTAREA", "SELECT"].includes(document.activeElement.tagName)) {
    event.preventDefault();
    siteSearch.focus();
  }
});

const gradeToPercent = {
  12: "90-100%",
  11: "85-89%",
  10: "80-84%",
  9: "77-79%",
  8: "73-76%",
  7: "70-72%",
  6: "67-69%",
  5: "63-66%",
  4: "60-62%",
  3: "57-59%",
  2: "53-56%",
  1: "50-52%",
  0: "0-49%",
};

function createGpaRow(index) {
  const row = document.createElement("div");
  row.className = "gpa-row";
  row.innerHTML = `
    <label>Course
      <input name="course-${index}" placeholder="PHYSICS 2G03">
    </label>
    <label>Units
      <input name="units-${index}" type="number" min="0" step="0.5" value="3">
    </label>
    <label>Grade
      <select name="grade-${index}">
        ${Object.keys(gradeToPercent).reverse().map((grade) => `<option value="${grade}">${grade}</option>`).join("")}
      </select>
    </label>
    <button class="icon-button" type="button" aria-label="Remove row">×</button>
  `;
  row.querySelector("button").addEventListener("click", () => row.remove());
  return row;
}

function initGpaTool() {
  const form = document.querySelector("#gpa-form");
  const rows = document.querySelector("#gpa-rows");
  const addButton = document.querySelector("#add-gpa-row");
  const result = document.querySelector("#gpa-result");
  if (!form || !rows || !addButton || !result) return;

  let rowCount = 0;
  const addRow = () => rows.appendChild(createGpaRow(rowCount++));
  addRow();
  addRow();
  addRow();

  addButton.addEventListener("click", addRow);
  form.addEventListener("submit", (event) => {
    event.preventDefault();
    let points = 0;
    let units = 0;

    rows.querySelectorAll(".gpa-row").forEach((row) => {
      const unitValue = Number(row.querySelector('input[name^="units"]').value);
      const gradeValue = Number(row.querySelector("select").value);
      if (Number.isFinite(unitValue) && unitValue > 0 && Number.isFinite(gradeValue)) {
        points += unitValue * gradeValue;
        units += unitValue;
      }
    });

    if (units <= 0) {
      result.innerHTML = `<span>Result</span><strong>--</strong><p>Add at least one course with units greater than zero.</p>`;
      return;
    }

    const gpa = points / units;
    const nearest = Math.max(0, Math.min(12, Math.round(gpa)));
    result.innerHTML = `<span>Result</span><strong>${gpa.toFixed(2)}</strong><p>${units.toFixed(1)} units counted. Nearest percentage band: ${gradeToPercent[nearest]}.</p>`;
  });
}

function initRequirementsTool() {
  const form = document.querySelector("#requirements-form");
  const textarea = document.querySelector("#completed-courses");
  const setSelect = document.querySelector("#requirement-set");
  const result = document.querySelector("#requirements-result");
  if (!form || !textarea || !result) return;

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const courses = textarea.value.split(/[\n,;]+/).map((item) => item.trim()).filter(Boolean);
    const response = await fetch("/api/requirements/check", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ courses, requirement_set: setSelect ? setSelect.value : "level-ii-admission" }),
    });
    const data = await response.json();
    result.innerHTML = data.results.map((item) => {
      const label = item.status.replace("-", " ");
      return `
        <div class="status-row ${item.status}">
          <span class="status-pill">${label}</span>
          <strong>${item.label}</strong>
          <p>${item.description}</p>
          ${item.required_units ? `<p><small>${item.matched_units}/${item.required_units} units matched</small></p>` : ""}
          ${item.note ? `<p><small>${item.note}</small></p>` : ""}
        </div>
      `;
    }).join("");
  });
}

function initProgramTool() {
  const form = document.querySelector("#program-form");
  const textarea = document.querySelector("#program-courses");
  const manualInput = document.querySelector("#program-manual-courses");
  const result = document.querySelector("#program-result");
  const selectedCount = document.querySelector("#selected-count");
  const clearButton = document.querySelector("#clear-program-selection");
  const sampleButton = document.querySelector("#load-sample-outline");
  if (!form || !textarea || !result) return;

  const chips = Array.from(form.querySelectorAll(".course-chip input"));

  const normalizeCourse = (value) => String(value || "").toUpperCase().replace(/[-\s]/g, "");
  const manualCourses = () => manualInput ? manualInput.value.split(/[\n,;]+/).map(normalizeCourse).filter(Boolean) : [];
  const selectedCourses = () => Array.from(new Set([
    ...chips.filter((chip) => chip.checked).map((chip) => normalizeCourse(chip.value)),
    ...manualCourses(),
  ]));

  const syncCourse = (code, checked) => {
    chips.filter((chip) => normalizeCourse(chip.value) === code).forEach((chip) => {
      chip.checked = checked;
      chip.closest(".course-chip")?.classList.toggle("selected", checked);
    });
  };

  const updateSelectedState = () => {
    chips.forEach((chip) => chip.closest(".course-chip")?.classList.toggle("selected", chip.checked));
    const courses = selectedCourses();
    textarea.value = courses.join(", ");
    if (selectedCount) selectedCount.textContent = String(courses.length);
  };

  chips.forEach((chip) => {
    chip.addEventListener("change", () => {
      syncCourse(normalizeCourse(chip.value), chip.checked);
      updateSelectedState();
    });
  });

  if (manualInput) {
    manualInput.addEventListener("input", updateSelectedState);
  }

  if (clearButton) {
    clearButton.addEventListener("click", () => {
      chips.forEach((chip) => {
        chip.checked = false;
      });
      if (manualInput) manualInput.value = "";
      updateSelectedState();
    });
  }

  if (sampleButton) {
    sampleButton.addEventListener("click", () => {
      const sampleCodes = new Set(String(sampleButton.dataset.courses || "").split(",").map(normalizeCourse).filter(Boolean));
      chips.forEach((chip) => {
        chip.checked = sampleCodes.has(normalizeCourse(chip.value));
      });
      if (manualInput) {
        const covered = new Set(chips.map((chip) => normalizeCourse(chip.value)));
        manualInput.value = Array.from(sampleCodes).filter((code) => !covered.has(code)).join(", ");
      }
      updateSelectedState();
      form.requestSubmit();
    });
  }

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    updateSelectedState();
    const courses = selectedCourses();
    const response = await fetch("/api/program/check", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ courses }),
    });
    const data = await response.json();
    result.innerHTML = Object.entries(data.groups).map(([group, items]) => `
      <div class="status-group">
        <h3>${formatLabel(group)}</h3>
        ${items.map((item) => `
          <div class="status-row ${item.status}">
            <span class="status-pill">${item.status.replace("-", " ")}</span>
            <strong>${item.label}</strong>
            <p>${item.description}</p>
            ${item.required_units ? `<p><small>${item.matched_units}/${item.required_units} units matched</small></p>` : ""}
            ${item.matched && item.matched.length ? `<p><small>Matched: ${item.matched.join(", ")}</small></p>` : ""}
            ${item.note ? `<p><small>${item.note}</small></p>` : ""}
          </div>
        `).join("")}
      </div>
    `).join("");
  });

  updateSelectedState();
}

function formatLabel(value) {
  return String(value)
    .replaceAll("-", " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase())
    .replace(/\bIii\b/g, "III")
    .replace(/\bIi\b/g, "II")
    .replace(/\bIv\b/g, "IV");
}

function initEmailTool() {
  const form = document.querySelector("#email-form");
  const output = document.querySelector("#email-result");
  if (!form || !output) return;

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const payload = Object.fromEntries(new FormData(form).entries());
    const response = await fetch("/api/cold-email", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await response.json();
    output.textContent = data.body;
  });
}

function initChatComposer() {
  document.querySelectorAll("[data-chat-composer]").forEach((form) => {
    const input = form.querySelector("[data-chat-input]");
    const fileInput = form.querySelector("[data-file-input]");
    const fileList = form.querySelector("[data-file-list]");
    if (!input) return;

    const resizeInput = () => {
      input.style.height = "auto";
      input.style.height = `${Math.min(input.scrollHeight, 132)}px`;
    };

    const updateFiles = () => {
      if (!fileInput || !fileList) return;
      const files = Array.from(fileInput.files || []);
      fileList.innerHTML = "";
      fileList.classList.toggle("has-files", files.length > 0);
      files.slice(0, 4).forEach((file) => {
        const item = document.createElement("span");
        item.className = "chat-file-chip";
        item.innerHTML = `<strong>${escapeHtml(file.name)}</strong><small>${formatFileSize(file.size)}</small>`;
        fileList.appendChild(item);
      });
      if (files.length > 4) {
        const extra = document.createElement("span");
        extra.className = "chat-file-chip muted";
        extra.textContent = `${files.length - 4} more selected`;
        fileList.appendChild(extra);
      }
    };

    input.addEventListener("input", resizeInput);
    input.addEventListener("keydown", (event) => {
      if (event.key !== "Enter" || event.shiftKey || event.isComposing) return;
      event.preventDefault();
      if (input.value.trim() || (fileInput && fileInput.files.length)) {
        form.requestSubmit();
      }
    });

    if (fileInput) {
      fileInput.addEventListener("change", updateFiles);
    }
    resizeInput();
    updateFiles();
  });
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function formatFileSize(bytes) {
  if (!Number.isFinite(bytes)) return "";
  if (bytes >= 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  return `${Math.max(1, Math.round(bytes / 1024))} KB`;
}

initGpaTool();
initRequirementsTool();
initProgramTool();
initEmailTool();
initChatComposer();
