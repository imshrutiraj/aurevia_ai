/**
 * Aurevia AI - Client-side Architecture & API Integration
 * Connects all 9 modules with Python/Flask backend and AI/ML services.
 */

// Application State
const state = {
  resumeId: null,
  filename: null,
  targetRole: "Software Development Engineer",
  analysisData: null,
  activeModule: "analyzer"
};

// -----------------------------------------------------------------------------
// INITIALIZATION & EVENT LISTENERS
// -----------------------------------------------------------------------------
document.addEventListener("DOMContentLoaded", function () {
  initNavigation();
  init3DEffect();
  initUploadForm();
  initDragAndDrop();
  loadDashboardData();
  loadAnalysisHistory();
});

// Toast notification helper
function showToast(message, type = "success") {
  const container = document.getElementById("toastContainer");
  if (!container) return;
  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.innerHTML = `<span>${type === "success" ? "✓" : "⚠"}</span> <div>${escapeHTML(message)}</div>`;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateX(100%)";
    toast.style.transition = "all 0.3s ease";
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

// -----------------------------------------------------------------------------
// NAVIGATION & MODULE SWITCHING
// -----------------------------------------------------------------------------
function initNavigation() {
  const navBtns = document.querySelectorAll(".mod-nav-btn");
  navBtns.forEach((btn) => {
    btn.addEventListener("click", function () {
      const targetMod = this.getAttribute("data-module");
      switchModule(targetMod);
    });
  });
}

function switchModule(moduleName) {
  state.activeModule = moduleName;

  // Update navbar buttons
  document.querySelectorAll(".mod-nav-btn").forEach((btn) => {
    if (btn.getAttribute("data-module") === moduleName) {
      btn.classList.add("active");
    } else {
      btn.classList.remove("active");
    }
  });

  // Hide all panels
  document.querySelectorAll(".module-panel").forEach((panel) => {
    panel.classList.remove("active-panel");
  });

  // Show selected panel
  const activePanel = document.getElementById(`panel-${moduleName}`);
  if (activePanel) {
    activePanel.classList.add("active-panel");
    activePanel.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  // Auto trigger module refresh if needed
  if (moduleName === "dashboard") {
    loadDashboardData();
  } else if (moduleName === "interview" && state.resumeId) {
    // If questions not yet generated, generate automatically
    const container = document.getElementById("interviewQuestionsList");
    if (container && container.children.length === 0) {
      generateMockInterviewQuestions();
    }
  }
}

function goToAnalyzer() {
  switchModule("analyzer");
}

function goToFeatures() {
  document.getElementById("features").scrollIntoView({ behavior: "smooth" });
}

// -----------------------------------------------------------------------------
// 3D HERO INTERACTION
// -----------------------------------------------------------------------------
function init3DEffect() {
  const visual = document.getElementById("visual");
  const coreWrap = document.getElementById("coreWrap");

  if (!visual || !coreWrap) return;

  visual.addEventListener("mousemove", function (event) {
    if (window.innerWidth < 760) return;
    const rect = visual.getBoundingClientRect();
    const x = (event.clientX - rect.left) / rect.width - 0.5;
    const y = (event.clientY - rect.top) / rect.height - 0.5;
    coreWrap.style.transform = `translateY(-8px) rotateY(${x * 24}deg) rotateX(${-y * 20}deg)`;
  });

  visual.addEventListener("mouseleave", function () {
    coreWrap.style.transform = "";
  });
}

// -----------------------------------------------------------------------------
// RESUME UPLOAD & ANALYSIS SUBMISSION
// -----------------------------------------------------------------------------
function initDragAndDrop() {
  const dropArea = document.getElementById("fileDropArea");
  const fileInput = document.getElementById("resume");

  if (!dropArea || !fileInput) return;

  ["dragenter", "dragover"].forEach((eventName) => {
    dropArea.addEventListener(eventName, (e) => {
      e.preventDefault();
      dropArea.classList.add("dragover");
    });
  });

  ["dragleave", "drop"].forEach((eventName) => {
    dropArea.addEventListener(eventName, (e) => {
      e.preventDefault();
      dropArea.classList.remove("dragover");
    });
  });

  dropArea.addEventListener("drop", (e) => {
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      fileInput.files = files;
      updateFileLabel(files[0].name);
    }
  });

  fileInput.addEventListener("change", function () {
    if (this.files.length > 0) {
      updateFileLabel(this.files[0].name);
    }
  });
}

function updateFileLabel(fileName) {
  const label = document.getElementById("fileNameDisplay");
  if (label) {
    label.innerHTML = `<strong>Selected:</strong> <span style="color:var(--gold);">${escapeHTML(fileName)}</span>`;
  }
}

function initUploadForm() {
  const form = document.getElementById("resumeForm");
  if (!form) return;

  form.addEventListener("submit", async function (event) {
    event.preventDefault();

    const fileInput = document.getElementById("resume");
    const roleSelect = document.getElementById("role");
    const jdInput = document.getElementById("jobDescription");
    const submitBtn = document.getElementById("analyzeSubmitBtn");
    const statusBox = document.getElementById("uploadStatusMessage");

    const file = fileInput.files[0];
    const role = roleSelect.value;
    const jobDescription = jdInput.value.trim();

    if (!file) {
      showToast("Please choose a PDF or DOCX resume to upload.", "error");
      return;
    }

    state.targetRole = role;

    // Loading UI
    submitBtn.disabled = true;
    submitBtn.innerHTML = `<span>⏳</span> Analyzing with AI Pipeline...`;
    statusBox.style.display = "block";
    statusBox.innerHTML = `
      <div style="display:flex;align-items:center;gap:12px;">
        <div class="dot" style="animation: starsMove 1s linear infinite;"></div>
        <div>
          <strong style="color:var(--gold)">Running Multi-Module AI Pipeline...</strong><br>
          <span style="font-size:12px;color:var(--muted)">Extracting document text · NLP Named Entities · Scikit-learn Job Match · ATS Scoring</span>
        </div>
      </div>
    `;

    const formData = new FormData();
    formData.append("resume", file);
    formData.append("target_role", role);
    formData.append("job_description", jobDescription);

    try {
      const response = await fetch("/api/analyze", {
        method: "POST",
        body: formData
      });

      const data = await response.json();

      if (!response.ok || !data.success) {
        throw new Error(data.error || "Analysis failed.");
      }

      state.resumeId = data.resume_id;
      state.filename = file.name;
      state.analysisData = data;

      showToast("Analysis complete! All 9 modules updated with live AI intelligence.", "success");
      statusBox.style.display = "none";

      // Update UI with real data across all modules
      populateAllModules(data);

      // Switch to Career Dashboard or Resume Intelligence
      switchModule("dashboard");

    } catch (err) {
      statusBox.innerHTML = `<span style="color:var(--danger)">⚠ Error: ${escapeHTML(err.message)}</span>`;
      showToast(err.message, "error");
    } finally {
      submitBtn.disabled = false;
      submitBtn.innerHTML = `Analyze my career ↗`;
    }
  });
}

// -----------------------------------------------------------------------------
// POPULATE ALL 9 MODULES WITH REAL BACKEND DATA
// -----------------------------------------------------------------------------
function populateAllModules(data) {
  // Update Active Context Banner
  document.querySelectorAll(".active-resume-name").forEach((el) => {
    el.textContent = state.filename || "Uploaded Resume";
  });
  document.querySelectorAll(".active-target-role").forEach((el) => {
    el.textContent = data.target_role || state.targetRole;
  });

  // MODULE 1: RESUME INTELLIGENCE
  populateResumeIntelligence(data);

  // MODULE 2: ATS SCORE
  populateATSScore(data.ats_analysis);

  // MODULE 3: JOB MATCH EXPLORER
  populateJobMatch(data.job_match);

  // MODULE 4: SKILL GAP DETECTOR
  populateSkillGaps(data.skill_gaps);

  // MODULE 5: AI RESUME IMPROVER
  populateResumeImprover(data.resume_improver);

  // MODULE 6: LEARNING ROADMAP
  populateLearningRoadmap(data.learning_roadmap);

  // MODULE 8: PRE-POPULATE COVER LETTER FORM
  const clRole = document.getElementById("clTargetRole");
  if (clRole) clRole.value = data.target_role;

  // MODULE 9: DASHBOARD
  loadDashboardData();
}

// MODULE 1: Resume Intelligence
function populateResumeIntelligence(data) {
  // Fetch parsed resume details
  if (!state.resumeId) return;

  fetch(`/api/dashboard?analysis_id=${data.analysis_id}`)
    .then((r) => r.json())
    .then((res) => {
      if (!res.success) return;
      const d = res.dashboard;

      const nameEl = document.getElementById("candidateNameDisplay");
      if (nameEl) nameEl.textContent = data.candidate_name || "Candidate";

      // Summary
      const summaryEl = document.getElementById("resumeSummaryDisplay");
      if (summaryEl && data.resume_improver) {
        summaryEl.textContent = data.resume_improver.summary_comparison.after;
      }

      // Matched & Categorized Skills
      const skillsContainer = document.getElementById("extractedSkillsContainer");
      if (skillsContainer && d.matched_skills) {
        skillsContainer.innerHTML = d.matched_skills
          .map((s) => `<span class="skill-pill matched">✓ ${escapeHTML(s)}</span>`)
          .join(" ");
      }
    });
}

// MODULE 2: ATS Score
function populateATSScore(ats) {
  if (!ats) return;

  const scoreEl = document.getElementById("atsScoreNumber");
  if (scoreEl) scoreEl.textContent = `${Math.round(ats.total_ats_score)}`;

  const barEl = document.getElementById("atsScoreBar");
  if (barEl) barEl.style.width = `${ats.total_ats_score}%`;

  // Breakdown metrics
  const bd = ats.breakdown;
  if (bd) {
    setBreakdownScore("bdSectionComp", bd.section_completeness.score, bd.section_completeness.max);
    setBreakdownScore("bdKeywords", bd.keyword_relevance.score, bd.keyword_relevance.max);
    setBreakdownScore("bdQuant", bd.quantifiable_impact.score, bd.quantifiable_impact.max);
    setBreakdownScore("bdReadability", bd.readability_structure.score, bd.readability_structure.max);
  }

  // Checklist
  const checklistEl = document.getElementById("atsSectionChecklist");
  if (checklistEl && ats.section_checklist) {
    checklistEl.innerHTML = ats.section_checklist
      .map(
        (item) => `
        <div style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.06);">
          <span>${item.passed ? "✓" : "○"} ${escapeHTML(item.section)}</span>
          <span class="badge ${item.passed ? "badge-success" : "badge-danger"}">${item.status}</span>
        </div>
      `
      )
      .join("");
  }

  // Suggestions
  const suggEl = document.getElementById("atsSuggestionsList");
  if (suggEl && ats.suggestions) {
    suggEl.innerHTML = ats.suggestions
      .map((s) => `<li style="margin-bottom:6px;color:var(--ivory);">${escapeHTML(s)}</li>`)
      .join("");
  }
}

function setBreakdownScore(elementId, score, max) {
  const el = document.getElementById(elementId);
  if (el) el.textContent = `${score} / ${max}`;
}

// MODULE 3: Job Match Explorer
function populateJobMatch(jobMatch) {
  if (!jobMatch) return;

  const topRolesContainer = document.getElementById("topPredictedRolesList");
  if (topRolesContainer && jobMatch.top_predicted_roles) {
    topRolesContainer.innerHTML = jobMatch.top_predicted_roles
      .map(
        (role, i) => `
        <div class="stat-card" style="margin-bottom:12px;">
          <div style="display:flex;justify-content:space-between;align-items:center;">
            <div>
              <span class="badge badge-gold">#${i + 1} Predicted Fit</span>
              <h4 style="margin:6px 0;font-size:16px;">${escapeHTML(role.role)}</h4>
              <p style="font-size:12px;color:var(--muted)">Skill Coverage: ${role.skill_coverage_pct}%</p>
            </div>
            <div style="text-align:right;">
              <span style="font-size:24px;font-weight:800;color:var(--gold);">${role.confidence_score}%</span>
              <div style="font-size:10px;color:var(--muted)">Suitability</div>
            </div>
          </div>
          <div class="skills-wrap" style="margin-top:10px;">
            ${role.matched_skills.map((s) => `<span class="skill-pill matched">${escapeHTML(s)}</span>`).join(" ")}
            ${role.missing_skills.slice(0, 4).map((s) => `<span class="skill-pill missing">+ ${escapeHTML(s)}</span>`).join(" ")}
          </div>
        </div>
      `
      )
      .join("");
  }

  // Target Role Evaluation
  const evalData = jobMatch.target_role_evaluation;
  if (evalData) {
    const scoreEl = document.getElementById("targetRoleOverallMatch");
    if (scoreEl) scoreEl.textContent = `${evalData.overall_match_score}%`;
  }
}

// MODULE 4: Skill Gap Detector
function populateSkillGaps(gaps) {
  if (!gaps) return;

  const coverageEl = document.getElementById("skillCoveragePctDisplay");
  if (coverageEl) coverageEl.textContent = `${gaps.coverage_percentage}%`;

  const matchedCoreEl = document.getElementById("matchedCoreSkillsList");
  if (matchedCoreEl) {
    matchedCoreEl.innerHTML = gaps.matched_core_skills
      .map((s) => `<span class="skill-pill matched">✓ ${escapeHTML(s)}</span>`)
      .join(" ");
  }

  const missingCoreEl = document.getElementById("missingCoreSkillsList");
  if (missingCoreEl) {
    missingCoreEl.innerHTML = gaps.missing_core_skills
      .map((s) => `<span class="skill-pill missing">✕ ${escapeHTML(s)}</span>`)
      .join(" ");
  }

  const prioritizedEl = document.getElementById("prioritizedSkillsList");
  if (prioritizedEl && gaps.prioritized_recommendations) {
    prioritizedEl.innerHTML = gaps.prioritized_recommendations
      .map(
        (rec) => `
        <div style="padding:10px 14px;background:rgba(255,255,255,0.03);border:1px solid var(--border-light);border-radius:10px;margin-bottom:8px;">
          <div style="display:flex;justify-content:space-between;">
            <strong style="color:var(--gold);">${escapeHTML(rec.skill)}</strong>
            <span class="badge ${rec.priority === "High" ? "badge-danger" : "badge-lavender"}">${rec.priority} Priority</span>
          </div>
          <p style="font-size:12px;color:var(--muted);margin-top:4px;">${escapeHTML(rec.reason)}</p>
        </div>
      `
      )
      .join("");
  }
}

// MODULE 5: AI Resume Improver
function populateResumeImprover(improver) {
  if (!improver) return;

  // Summary Comparison
  const beforeSum = document.getElementById("improverSummaryBefore");
  const afterSum = document.getElementById("improverSummaryAfter");
  if (beforeSum) beforeSum.textContent = improver.summary_comparison.before;
  if (afterSum) afterSum.textContent = improver.summary_comparison.after;

  // Bullet points
  const bulletsContainer = document.getElementById("improverBulletsList");
  if (bulletsContainer && improver.bullet_enhancements) {
    bulletsContainer.innerHTML = improver.bullet_enhancements
      .map(
        (b, i) => `
        <div class="panel-card" style="margin-bottom:16px;padding:20px;">
          <div style="display:flex;justify-content:space-between;margin-bottom:8px;">
            <span class="badge badge-gold">Bullet Point #${i + 1}</span>
            <span style="font-size:11px;color:var(--muted);">${escapeHTML(b.detected_weakness)}</span>
          </div>
          <div class="comparison-container">
            <div class="comparison-box">
              <div class="comparison-header" style="color:var(--muted);">ORIGINAL</div>
              <p style="font-size:12px;">${escapeHTML(b.original)}</p>
            </div>
            <div class="comparison-box improved">
              <div class="comparison-header" style="color:var(--gold);">IMPROVED (ACTION-ORIENTED)</div>
              <p style="font-size:13px;font-weight:500;">${escapeHTML(b.improved)}</p>
              <button class="secondary-btn" style="padding:6px 12px;font-size:11px;margin-top:10px;" onclick="copyToClipboard('${escapeJSString(b.improved)}')">Copy Improved 📋</button>
            </div>
          </div>
        </div>
      `
      )
      .join("");
  }

  // Power Action Verbs
  const verbsEl = document.getElementById("powerActionVerbsList");
  if (verbsEl && improver.suggested_action_verbs) {
    verbsEl.innerHTML = improver.suggested_action_verbs
      .map((v) => `<span class="skill-pill" style="border-color:var(--gold);color:var(--gold-light);">+ ${escapeHTML(v)}</span>`)
      .join(" ");
  }
}

// MODULE 6: Learning Roadmap
function populateLearningRoadmap(roadmap) {
  if (!roadmap) return;

  renderMilestoneLevel("roadmapBeginnerList", roadmap.levels.beginner.milestones);
  renderMilestoneLevel("roadmapIntermediateList", roadmap.levels.intermediate.milestones);
  renderMilestoneLevel("roadmapAdvancedList", roadmap.levels.advanced.milestones);

  // Recommended Projects
  const projContainer = document.getElementById("roadmapProjectsList");
  if (projContainer && roadmap.recommended_projects) {
    projContainer.innerHTML = roadmap.recommended_projects
      .map(
        (p) => `
        <div class="stat-card" style="margin-bottom:12px;">
          <strong style="color:var(--gold);font-size:14px;">${escapeHTML(p.title)}</strong>
          <div style="font-size:11px;color:var(--lavender);margin:4px 0;">Skills: ${escapeHTML(p.skills)}</div>
          <p style="font-size:12px;color:var(--muted);">${escapeHTML(p.description)}</p>
        </div>
      `
      )
      .join("");
  }

  // Certifications
  const certContainer = document.getElementById("roadmapCertificationsList");
  if (certContainer && roadmap.target_certifications) {
    certContainer.innerHTML = roadmap.target_certifications
      .map((c) => `<div style="padding:10px;background:rgba(255,255,255,0.03);border:1px solid var(--border-light);border-radius:10px;margin-bottom:8px;font-size:13px;">🏆 ${escapeHTML(c)}</div>`)
      .join("");
  }
}

function renderMilestoneLevel(containerId, milestones) {
  const container = document.getElementById(containerId);
  if (!container || !milestones) return;

  container.innerHTML = milestones
    .map(
      (m, idx) => `
      <div class="milestone-item">
        <input type="checkbox" class="milestone-checkbox" onchange="trackRoadmapProgress()">
        <div style="flex:1;">
          <div style="display:flex;justify-content:space-between;align-items:center;">
            <strong style="font-size:13px;color:var(--ivory);">${escapeHTML(m.topic)}</strong>
            <span class="badge badge-lavender">${escapeHTML(m.duration)}</span>
          </div>
          <p style="font-size:12px;color:var(--muted);margin-top:4px;">${escapeHTML(m.description)}</p>
        </div>
      </div>
    `
    )
    .join("");
}

function trackRoadmapProgress() {
  const checkboxes = document.querySelectorAll(".milestone-checkbox");
  const total = checkboxes.length;
  if (total === 0) return;
  const checked = document.querySelectorAll(".milestone-checkbox:checked").length;
  const pct = Math.round((checked / total) * 100);

  const trackerEl = document.getElementById("roadmapProgressDisplay");
  if (trackerEl) trackerEl.textContent = `${pct}% Complete (${checked}/${total} topics)`;
}

// -----------------------------------------------------------------------------
// MODULE 7: AI MOCK INTERVIEW
// -----------------------------------------------------------------------------
async function generateMockInterviewQuestions() {
  const container = document.getElementById("interviewQuestionsList");
  if (!container) return;

  container.innerHTML = `
    <div style="text-align:center;padding:30px;color:var(--muted);">
      <div class="dot" style="margin:0 auto 10px;"></div>
      Generating personalized technical, behavioral and HR interview questions...
    </div>
  `;

  try {
    const res = await fetch("/api/interview/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        resume_id: state.resumeId,
        target_role: state.targetRole
      })
    });
    const data = await res.json();
    if (!data.success) throw new Error(data.error);

    renderInterviewQuestions(data.questions);
  } catch (err) {
    container.innerHTML = `<span style="color:var(--danger)">Failed to generate questions: ${escapeHTML(err.message)}</span>`;
  }
}

function renderInterviewQuestions(questions) {
  const container = document.getElementById("interviewQuestionsList");
  if (!container) return;

  container.innerHTML = questions
    .map(
      (q, idx) => `
      <div class="interview-card" id="qcard-${idx}">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
          <span class="badge badge-gold">${escapeHTML(q.category)}</span>
          <span style="font-size:11px;color:var(--muted);">Question ${idx + 1} of ${questions.length}</span>
        </div>
        <h4 style="font-size:15px;margin-bottom:14px;color:var(--ivory);line-height:1.6;">${escapeHTML(q.question)}</h4>
        
        <textarea id="answerInput-${idx}" placeholder="Type your answer here in detail... Explain concepts, tradeoffs, or examples."></textarea>
        
        <div style="display:flex;gap:10px;margin-top:12px;">
          <button class="primary-btn" style="padding:10px 18px;font-size:12px;" onclick="submitAnswerForEvaluation(${idx}, ${escapeJSONForAttribute(q)})">
            Submit Answer for AI Evaluation ↗
          </button>
        </div>

        <div id="evalResult-${idx}" style="display:none;" class="interview-evaluation-box"></div>
      </div>
    `
    )
    .join("");
}

async function submitAnswerForEvaluation(index, questionObj) {
  const answerInput = document.getElementById(`answerInput-${index}`);
  const evalResultBox = document.getElementById(`evalResult-${index}`);
  const answer = answerInput.value.trim();

  if (!answer) {
    showToast("Please type an answer before submitting.", "error");
    return;
  }

  evalResultBox.style.display = "block";
  evalResultBox.innerHTML = `<span style="color:var(--gold)">Evaluating answer semantics and concept coverage...</span>`;

  try {
    const res = await fetch("/api/interview/evaluate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        resume_id: state.resumeId,
        target_role: state.targetRole,
        category: questionObj.category,
        question: questionObj.question,
        user_answer: answer,
        key_concepts: questionObj.key_concepts,
        model_answer: questionObj.model_answer
      })
    });

    const data = await res.json();
    if (!data.success) throw new Error(data.error);

    const ev = data.evaluation;
    evalResultBox.innerHTML = `
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
        <strong style="color:var(--gold);">AI Evaluation Score: ${ev.overall_score}/100</strong>
        <span style="font-size:11px;color:var(--muted)">Relevance: ${ev.relevance_score}% | Clarity: ${ev.clarity_score}%</span>
      </div>
      <p style="font-size:13px;line-height:1.6;margin-bottom:10px;">${escapeHTML(ev.feedback)}</p>
      
      <div style="background:rgba(0,0,0,0.3);padding:12px;border-radius:10px;margin-top:10px;">
        <strong style="font-size:11px;color:var(--lavender);letter-spacing:1px;">EXEMPLARY BENCHMARK ANSWER:</strong>
        <p style="font-size:12px;color:var(--ivory);margin-top:4px;">${escapeHTML(ev.model_answer)}</p>
      </div>
    `;

    showToast("Answer evaluated successfully!", "success");
    loadDashboardData(); // Update interview readiness in dashboard
  } catch (err) {
    evalResultBox.innerHTML = `<span style="color:var(--danger)">Evaluation error: ${escapeHTML(err.message)}</span>`;
  }
}

// -----------------------------------------------------------------------------
// MODULE 8: COVER LETTER GENERATOR
// -----------------------------------------------------------------------------
async function generateCoverLetterAction() {
  const roleInput = document.getElementById("clTargetRole");
  const companyInput = document.getElementById("clCompany");
  const jdInput = document.getElementById("clJobDescription");
  const outputArea = document.getElementById("coverLetterOutput");
  const btn = document.getElementById("genCoverLetterBtn");

  const targetRole = roleInput.value.trim() || state.targetRole;
  const companyName = companyInput.value.trim() || "the Hiring Organization";
  const jobDescription = jdInput ? jdInput.value.trim() : "";

  btn.disabled = true;
  btn.textContent = "Generating Cover Letter...";

  try {
    const res = await fetch("/api/cover-letter/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        resume_id: state.resumeId,
        target_role: targetRole,
        company_name: companyName,
        job_description: jobDescription
      })
    });
    const data = await res.json();
    if (!data.success) throw new Error(data.error);

    outputArea.value = data.content;
    showToast("Cover letter generated and tailored to your resume!", "success");
  } catch (err) {
    showToast(err.message, "error");
  } finally {
    btn.disabled = false;
    btn.textContent = "Generate Personalized Cover Letter ↗";
  }
}

function copyCoverLetter() {
  const outputArea = document.getElementById("coverLetterOutput");
  if (!outputArea || !outputArea.value) {
    showToast("Generate a cover letter first before copying.", "error");
    return;
  }
  copyToClipboard(outputArea.value);
}

// -----------------------------------------------------------------------------
// MODULE 9: CAREER DASHBOARD
// -----------------------------------------------------------------------------
async function loadDashboardData() {
  try {
    let url = "/api/dashboard";
    if (state.resumeId) url += `?resume_id=${state.resumeId}`;

    const res = await fetch(url);
    const data = await res.json();
    if (!data.success) return;

    const d = data.dashboard;

    // Update stat numbers
    setStat("dashOverallScore", `${Math.round(d.overall_resume_score)}%`);
    setStat("dashATSScore", `${Math.round(d.ats_score)}%`);
    setStat("dashSkillsIdentified", `${d.total_skills_identified}`);
    setStat("dashSkillGaps", `${d.skill_gaps_count}`);
    setStat("dashInterviewReadiness", `${Math.round(d.interview_readiness_score)}%`);

    // Render charts
    if (d.charts && window.Plotly) {
      if (d.charts.ats_gauge) {
        const spec = JSON.parse(d.charts.ats_gauge);
        Plotly.newPlot("plotlyAtsGauge", spec.data, spec.layout, { responsive: true, displayModeBar: false });
      }
      if (d.charts.role_matches) {
        const spec = JSON.parse(d.charts.role_matches);
        Plotly.newPlot("plotlyRoleMatches", spec.data, spec.layout, { responsive: true, displayModeBar: false });
      }
    }

    if (d.charts && d.charts.skill_coverage_pie) {
      const pieImg = document.getElementById("matplotlibPieImage");
      if (pieImg) {
        pieImg.src = d.charts.skill_coverage_pie;
        pieImg.style.display = "block";
      }
    }
  } catch (err) {
    console.error("Dashboard data load error:", err);
  }
}

function setStat(id, val) {
  const el = document.getElementById(id);
  if (el) el.textContent = val;
}

// -----------------------------------------------------------------------------
// ADDITIONAL FEATURES (JD Analyzer, Comparison, History)
// -----------------------------------------------------------------------------
async function analyzeRawJobDescriptionAction() {
  const input = document.getElementById("rawJdInput");
  const resultBox = document.getElementById("rawJdResult");
  const text = input.value.trim();

  if (!text || text.length < 20) {
    showToast("Please paste a job description with at least 20 characters.", "error");
    return;
  }

  resultBox.style.display = "block";
  resultBox.innerHTML = `Extracting key skills, experience level, and requirements...`;

  try {
    const res = await fetch("/api/job-description/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ job_description: text })
    });
    const data = await res.json();
    if (!data.success) throw new Error(data.error);

    const a = data.analysis;
    resultBox.innerHTML = `
      <div style="margin-bottom:10px;">
        <strong>Experience Level:</strong> <span style="color:var(--gold);">${escapeHTML(a.experience_level)}</span><br>
        <strong>Education:</strong> <span style="color:var(--ivory);">${escapeHTML(a.education_requirements)}</span>
      </div>
      <strong>Key Skills Extracted (${a.total_skills_detected}):</strong>
      <div class="skills-wrap" style="margin-top:6px;">
        ${a.extracted_skills.map((s) => `<span class="skill-pill matched">${escapeHTML(s)}</span>`).join(" ")}
      </div>
    `;
  } catch (err) {
    resultBox.innerHTML = `<span style="color:var(--danger)">${escapeHTML(err.message)}</span>`;
  }
}

async function compareResumeVersionsAction() {
  const v1 = document.getElementById("v1TextInput").value.trim();
  const v2 = document.getElementById("v2TextInput").value.trim();
  const resultBox = document.getElementById("compareResultBox");

  if (!v1 || !v2) {
    showToast("Please provide text for both Version 1 and Version 2.", "error");
    return;
  }

  resultBox.style.display = "block";
  resultBox.innerHTML = `Comparing versions using semantic embeddings and keyword diffing...`;

  try {
    const res = await fetch("/api/resume/compare", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text_v1: v1, text_v2: v2 })
    });
    const data = await res.json();
    if (!data.success) throw new Error(data.error);

    const c = data.comparison;
    resultBox.innerHTML = `
      <div style="display:flex;justify-content:space-between;margin-bottom:12px;">
        <strong>Semantic Content Overlap: ${c.semantic_similarity_pct}%</strong>
        <span style="font-size:12px;color:var(--muted);">V1 Words: ${c.v1_word_count} | V2 Words: ${c.v2_word_count}</span>
      </div>
      <div>
        <strong>Newly Added Skills:</strong>
        <div class="skills-wrap" style="margin:6px 0 10px;">
          ${c.added_skills.length ? c.added_skills.map((s) => `<span class="skill-pill matched">+ ${escapeHTML(s)}</span>`).join(" ") : "<span style='font-size:12px;color:var(--muted)'>None</span>"}
        </div>
      </div>
      <div style="margin-top:10px;">
        <strong>Key Insights:</strong>
        <ul style="padding-left:18px;margin-top:4px;font-size:12px;color:var(--ivory);">
          ${c.insights.map((ins) => `<li>${escapeHTML(ins)}</li>`).join("")}
        </ul>
      </div>
    `;
  } catch (err) {
    resultBox.innerHTML = `<span style="color:var(--danger)">${escapeHTML(err.message)}</span>`;
  }
}

async function loadAnalysisHistory() {
  const tableBody = document.getElementById("historyTableBody");
  if (!tableBody) return;

  try {
    const res = await fetch("/api/history");
    const data = await res.json();
    if (!data.success || !data.history.length) {
      tableBody.innerHTML = `<tr><td colspan="6" style="text-align:center;color:var(--muted);padding:16px;">No previous analysis records found. Upload a resume to create one!</td></tr>`;
      return;
    }

    tableBody.innerHTML = data.history
      .map(
        (row) => `
        <tr style="border-bottom:1px solid rgba(255,255,255,0.06);text-align:left;">
          <td style="padding:10px 8px;">#${row.id}</td>
          <td style="padding:10px 8px;font-weight:600;color:var(--ivory);">${escapeHTML(row.filename)}</td>
          <td style="padding:10px 8px;color:var(--gold);">${escapeHTML(row.target_role)}</td>
          <td style="padding:10px 8px;font-weight:700;">${row.ats_score}%</td>
          <td style="padding:10px 8px;font-size:12px;color:var(--muted);">${row.created_at}</td>
          <td style="padding:10px 8px;">
            <a href="/api/export-report/${row.id}" target="_blank" class="secondary-btn" style="padding:4px 8px;font-size:10px;">Download Report 📥</a>
            <button class="secondary-btn" style="padding:4px 8px;font-size:10px;color:var(--danger);margin-left:4px;" onclick="deleteAnalysisRecord(${row.id})">Delete ✕</button>
          </td>
        </tr>
      `
      )
      .join("");
  } catch (err) {
    console.error("Failed to load history:", err);
  }
}

async function deleteAnalysisRecord(id) {
  if (!confirm(`Are you sure you want to delete analysis record #${id}?`)) return;

  try {
    const res = await fetch(`/api/analysis/${id}`, { method: "DELETE" });
    const data = await res.json();
    if (data.success) {
      showToast(data.message, "success");
      loadAnalysisHistory();
    }
  } catch (err) {
    showToast("Failed to delete record.", "error");
  }
}

// -----------------------------------------------------------------------------
// AURE AI CHAT COMPANION (BACKEND INTEGRATED)
// -----------------------------------------------------------------------------
function addChatMessage(message, type) {
  const chat = document.getElementById("chatMessages");
  if (!chat) return;
  const div = document.createElement("div");
  div.className = "message " + type;
  div.innerHTML = message;
  chat.appendChild(div);
  chat.scrollTop = chat.scrollHeight;
}

function askAure(question) {
  document.getElementById("aureInput").value = question;
  sendAureMessage();
}

async function sendAureMessage() {
  const input = document.getElementById("aureInput");
  const question = input.value.trim();
  if (!question) return;

  addChatMessage(escapeHTML(question), "user");
  input.value = "";

  // Show typing dot
  const tempId = "aureTypingIndicator";
  addChatMessage('<span id="' + tempId + '">Aure is thinking... ✦</span>', "bot");

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: question,
        resume_id: state.resumeId
      })
    });
    const data = await res.json();

    const typingEl = document.getElementById(tempId);
    if (typingEl && typingEl.parentElement) {
      typingEl.parentElement.innerHTML = data.reply;
    }
  } catch (err) {
    const typingEl = document.getElementById(tempId);
    if (typingEl && typingEl.parentElement) {
      typingEl.parentElement.innerHTML = "I had trouble connecting to the backend. Please ensure the Flask server is running.";
    }
  }
}

function handleChatKey(event) {
  if (event.key === "Enter") {
    sendAureMessage();
  }
}

// -----------------------------------------------------------------------------
// UTILITIES
// -----------------------------------------------------------------------------
function copyToClipboard(text) {
  navigator.clipboard.writeText(text).then(() => {
    showToast("Copied to clipboard!", "success");
  }).catch(() => {
    showToast("Failed to copy.", "error");
  });
}

function escapeHTML(value) {
  if (!value) return "";
  return String(value).replace(/[&<>"']/g, function (char) {
    return {
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&#39;"
    }[char];
  });
}

function escapeJSString(str) {
  if (!str) return "";
  return str.replace(/'/g, "\\'").replace(/"/g, '\\"').replace(/\n/g, "\\n");
}

function escapeJSONForAttribute(obj) {
  return JSON.stringify(obj).replace(/"/g, '&quot;');
}
