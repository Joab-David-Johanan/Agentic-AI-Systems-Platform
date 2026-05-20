const workflowNodes = [
  {
    id: "query",
    label: "Query intake",
    detail: "Normalize request and create run metadata",
    lane: "input",
    icon: "Q",
  },
  {
    id: "guardrails",
    label: "Prompt guardrails",
    detail: "Injection, spam, and schema checks",
    lane: "safety",
    icon: "S",
  },
  {
    id: "model",
    label: "Model routing",
    detail: "OpenAI or Groq model factory",
    lane: "routing",
    icon: "M",
  },
  {
    id: "agent",
    label: "Agent routing",
    detail: "LangChain agent or LangGraph graph",
    lane: "routing",
    icon: "A",
  },
  {
    id: "tools",
    label: "Tool execution",
    detail: "Search, scrape, validation, retries",
    lane: "action",
    icon: "T",
  },
  {
    id: "summary",
    label: "Synthesis chain",
    detail: "Writer and critic pass",
    lane: "synthesis",
    icon: "W",
  },
  {
    id: "answer",
    label: "Final response",
    detail: "Answer, tools used, trace metadata",
    lane: "output",
    icon: "R",
  },
];

const state = {
  runtime: "langchain",
  provider: "openai",
  depth: 4,
  strictGuardrails: true,
  running: false,
  token: 0,
};

const elements = {
  form: document.querySelector("#workflow-form"),
  graph: document.querySelector("#workflow-graph"),
  eventList: document.querySelector("#event-list"),
  question: document.querySelector("#question"),
  depth: document.querySelector("#retrieval-depth"),
  depthValue: document.querySelector("#depth-value"),
  strictGuardrails: document.querySelector("#strict-guardrails"),
  reset: document.querySelector("#reset-run"),
  start: document.querySelector("#start-run"),
  runTitle: document.querySelector("#run-title"),
  runStatus: document.querySelector("#run-status"),
  summaryRuntime: document.querySelector("#summary-runtime"),
  summaryProvider: document.querySelector("#summary-provider"),
  summaryNode: document.querySelector("#summary-node"),
  finalAnswer: document.querySelector("#final-answer"),
  metricGuardrails: document.querySelector("#metric-guardrails"),
  metricRuntime: document.querySelector("#metric-runtime"),
  metricProvider: document.querySelector("#metric-provider"),
};

function wait(duration) {
  return new Promise((resolve) => window.setTimeout(resolve, duration));
}

function now() {
  return new Intl.DateTimeFormat("en", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  }).format(new Date());
}

function renderGraph() {
  elements.graph.innerHTML = workflowNodes
    .map(
      (node, index) => `
        <div class="graph-step-wrap">
          <article class="graph-step" id="node-${node.id}" data-state="pending">
            <div class="step-icon" aria-hidden="true">${node.icon}</div>
            <div>
              <p>${node.lane}</p>
              <h3>${node.label}</h3>
              <span>${node.detail}</span>
            </div>
          </article>
          ${index < workflowNodes.length - 1 ? `<div class="connector" id="connector-${node.id}" data-state="pending"></div>` : ""}
        </div>
      `,
    )
    .join("");
}

function syncSelections() {
  document.querySelectorAll("[data-control='runtime'] button").forEach((button) => {
    button.classList.toggle("selected", button.dataset.value === state.runtime);
  });
  document.querySelectorAll("[data-control='provider'] button").forEach((button) => {
    button.classList.toggle("selected", button.dataset.value === state.provider);
  });

  elements.runTitle.textContent =
    state.runtime === "langgraph" ? "Graph-based agent run" : "LangChain agent run";
  elements.summaryRuntime.textContent = state.runtime;
  elements.summaryProvider.textContent = state.provider;
  elements.metricRuntime.textContent = state.runtime;
  elements.metricProvider.textContent = state.provider;
  elements.metricGuardrails.textContent = state.strictGuardrails ? "Strict" : "Balanced";
  elements.depthValue.textContent = state.depth;
}

function setRunStatus(label, mode) {
  elements.runStatus.dataset.state = mode;
  elements.runStatus.querySelector("span:last-child").textContent = label;
}

function resetGraph() {
  workflowNodes.forEach((node) => {
    document.querySelector(`#node-${node.id}`).dataset.state = "pending";
    const connector = document.querySelector(`#connector-${node.id}`);
    if (connector) connector.dataset.state = "pending";
  });
  elements.summaryNode.textContent = "none";
}

function addEvent(node, status) {
  const messages = {
    query: `Question accepted with ${state.depth} retrieval passes configured.`,
    guardrails: state.strictGuardrails
      ? "Strict guardrails checked prompt injection, spam, and schema risks."
      : "Balanced guardrails checked the prompt before routing.",
    model: `${state.provider.toUpperCase()} selected through the lazy model factory.`,
    agent: `${state.runtime === "langgraph" ? "LangGraph graph" : "LangChain agent"} selected for this run.`,
    tools: "Search and scrape tools prepared with schema validation.",
    summary: "Writer and critic chains prepared for answer synthesis.",
    answer: "Final response assembled with trace and tool metadata.",
  };

  if (elements.eventList.querySelector(".empty-state")) {
    elements.eventList.innerHTML = "";
  }

  const item = document.createElement("article");
  item.className = "event-item";
  item.dataset.status = status;
  item.innerHTML = `
    <span aria-hidden="true">${status === "running" ? "..." : "ok"}</span>
    <div>
      <div class="event-meta">
        <strong>${node.label}</strong>
        <time>${now()}</time>
      </div>
      <p>${messages[node.id]}</p>
    </div>
  `;
  elements.eventList.prepend(item);
}

async function runWorkflow() {
  if (state.running || !elements.question.value.trim()) return;

  state.running = true;
  state.token += 1;
  const token = state.token;

  elements.start.disabled = true;
  elements.finalAnswer.textContent =
    "The final answer will appear here after the synthesis node completes.";
  elements.eventList.innerHTML = "";
  resetGraph();
  setRunStatus("Running", "running");

  for (const node of workflowNodes) {
    if (state.token !== token) return;

    const nodeElement = document.querySelector(`#node-${node.id}`);
    nodeElement.dataset.state = "running";
    elements.summaryNode.textContent = node.id;
    addEvent(node, "running");

    await wait(node.id === "tools" ? 850 : 650);

    nodeElement.dataset.state = "completed";
    const connector = document.querySelector(`#connector-${node.id}`);
    if (connector) connector.dataset.state = "completed";
    addEvent(node, "completed");
    await wait(180);
  }

  elements.summaryNode.textContent = "none";
  elements.finalAnswer.textContent = `${
    state.runtime === "langgraph" ? "Graph" : "Agent"
  } run completed with ${state.provider.toUpperCase()} routing, validated tool schemas, and a synthesis trace ready for the backend pipeline.`;
  state.running = false;
  elements.start.disabled = false;
  setRunStatus("Ready for next run", "idle");
}

function resetRun() {
  state.token += 1;
  state.running = false;
  elements.start.disabled = false;
  elements.eventList.innerHTML = `<p class="empty-state">Run the workflow to stream node-level events.</p>`;
  elements.finalAnswer.textContent =
    "The final answer will appear here after the synthesis node completes.";
  resetGraph();
  setRunStatus("Idle", "idle");
}

document.querySelectorAll(".segmented-control button").forEach((button) => {
  button.addEventListener("click", () => {
    const parent = button.closest(".segmented-control");
    state[parent.dataset.control] = button.dataset.value;
    syncSelections();
  });
});

elements.depth.addEventListener("input", (event) => {
  state.depth = Number(event.target.value);
  syncSelections();
});

elements.strictGuardrails.addEventListener("change", (event) => {
  state.strictGuardrails = event.target.checked;
  syncSelections();
});

elements.form.addEventListener("submit", (event) => {
  event.preventDefault();
  runWorkflow();
});

elements.reset.addEventListener("click", resetRun);

renderGraph();
syncSelections();
