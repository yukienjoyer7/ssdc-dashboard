import {
  FrontendRenderer,
  FrontendRendererArgs,
} from "@streamlit/component-v2-lib";
import "@carbon/web-components/es/components/button/index.js";
import "@carbon/web-components/es/components/data-table/index.js";
import "@carbon/web-components/es/components/date-picker/index.js";
import "@carbon/web-components/es/components/notification/index.js";
import "@carbon/web-components/es/components/pagination/index.js";
import "@carbon/web-components/es/components/select/index.js";
import "@carbon/web-components/es/components/tag/index.js";
import "@carbon/web-components/es/components/tile/index.js";
import "@carbon/web-components/es/components/ui-shell/index.js";
import "./styles.css";

type Option = { value: string; label: string };
type Page = { slug: string; title: string; icon: string };
type FilterValues = {
  date_start: string;
  date_end: string;
  company: string;
  study_program: string;
  request_status: string;
  placement_type: string;
};
type TableColumn = { key: string; label: string };
type TableRow = Record<string, string | number | boolean | null>;
type DetailItem = { label: string; value: string };
type ComponentData = {
  view: "shell" | "filters" | "kpis" | "feedback" | "data_status" | "table";
  pages?: Page[];
  active_page?: string;
  options?: Record<string, Option[]>;
  filters?: FilterValues;
  items?: Array<{ label: string; value: string; help?: string }>;
  kind?: "info" | "warning" | "error" | "success";
  title?: string;
  subtitle?: string;
  mode?: "local" | "prototype";
  record_count?: number;
  as_of_date?: string;
  kpi_status?: "provisional" | "validated";
  detail_items?: DetailItem[];
  warnings?: string[];
  rows?: TableRow[];
  columns?: TableColumn[];
  page?: number;
  page_size?: number;
  total_pages?: number;
  total_rows?: number;
  row_offset?: number;
  empty_title?: string;
  empty_detail?: string;
};

const rootFor = (parentElement: FrontendRendererArgs["parentElement"]) => {
  const root = parentElement.querySelector<HTMLElement>(".component-root");
  if (!root) throw new Error("Carbon component root not found");
  return root;
};

const carbon = (tag: string, text?: string) => {
  const node = document.createElement(tag);
  if (text) node.textContent = text;
  return node;
};

const emit = (args: FrontendRendererArgs, payload: Record<string, unknown>) => {
  args.setTriggerValue("action", payload);
};

const optionSelect = (
  key: string,
  label: string,
  values: Option[],
  selected: string,
) => {
  const wrapper = document.createElement("div");
  wrapper.className = "filter-control";
  const select = carbon("cds-select") as HTMLElement & { value?: string };
  select.setAttribute("id", key);
  select.setAttribute("label-text", label);
  select.setAttribute("value", selected);
  values.forEach((option) => {
    const item = carbon("cds-select-item", option.label) as HTMLElement & {
      value?: string;
    };
    item.setAttribute("value", option.value);
    if (option.value === selected) item.setAttribute("selected", "");
    select.appendChild(item);
  });
  wrapper.appendChild(select);
  return { wrapper, select };
};

const renderShell = (
  root: HTMLElement,
  data: ComponentData,
  args: FrontendRendererArgs,
) => {
  const header = carbon("cds-header") as HTMLElement;
  header.setAttribute("aria-label", "SSDC dashboard");
  const menu = carbon("cds-header-menu-button") as HTMLElement;
  menu.setAttribute("button-label-inactive", "Open navigation menu");
  menu.setAttribute("button-label-active", "Close navigation menu");
  const name = carbon("cds-header-name", "SSDC 2026") as HTMLElement;
  name.setAttribute("href", "#main-content");
  header.append(menu, name);

  const sideNav = carbon("cds-side-nav") as HTMLElement;
  sideNav.setAttribute("aria-label", "Dashboard navigation");
  sideNav.setAttribute("expanded", "");
  const items = carbon("cds-side-nav-items");
  (data.pages ?? []).forEach((page) => {
    const link = carbon("cds-side-nav-link", page.title) as HTMLElement;
    link.setAttribute("href", `#${page.slug}`);
    link.dataset.page = page.slug;
    link.setAttribute("title", page.title);
    if (page.slug === data.active_page) link.setAttribute("active", "");
    items.appendChild(link);
  });
  sideNav.appendChild(items);
  root.append(header, sideNav);

  const onMenu = () => {
    const open = sideNav.hasAttribute("expanded");
    sideNav.toggleAttribute("expanded", !open);
    menu.toggleAttribute("active", !open);
  };
  menu.addEventListener("cds-header-menu-button-toggled", onMenu);

  const onNavigate = (event: Event) => {
    const target = event.target as HTMLElement;
    const page = target.closest<HTMLElement>("[data-page]")?.dataset.page;
    if (!page) return;
    event.preventDefault();
    emit(args, { type: "navigate", page });
  };
  sideNav.addEventListener("click", onNavigate);

  return () => {
    menu.removeEventListener("cds-header-menu-button-toggled", onMenu);
    sideNav.removeEventListener("click", onNavigate);
  };
};

const renderFilters = (
  root: HTMLElement,
  data: ComponentData,
  args: FrontendRendererArgs,
) => {
  const filters = data.filters as FilterValues;
  const container = document.createElement("div");
  container.className = "cds-filter-container";
  const toolbar = document.createElement("div");
  toolbar.className = "cds-filter-toolbar";
  const content = document.createElement("div");
  content.className = "cds-filter-toolbar__content";
  const title = document.createElement("strong");
  title.className = "cds-filter-toolbar__title";
  title.textContent = "Global filters";
  const summary = document.createElement("div");
  summary.className = "cds-filter-toolbar__summary";
  const summaryValues = document.createElement("span");
  summaryValues.className = "cds-filter-toolbar__summary-values";
  const activeValues = [filters.company, filters.study_program];
  [filters.request_status, filters.placement_type].forEach((value) => {
    if (value && !value.startsWith("All ")) activeValues.push(value);
  });
  summaryValues.textContent = activeValues.join(" · ");
  const summarySeparator = document.createElement("span");
  summarySeparator.className = "cds-filter-toolbar__summary-separator";
  summarySeparator.setAttribute("aria-hidden", "true");
  summarySeparator.textContent = " · ";
  const summaryDate = document.createElement("span");
  summaryDate.className = "cds-filter-toolbar__summary-date";
  summaryDate.textContent =
    [filters.date_start, filters.date_end].filter(Boolean).join(" to ") ||
    "All dates";
  summary.append(summaryValues, summarySeparator, summaryDate);
  content.append(title, summary);

  const actions = document.createElement("div");
  actions.className = "cds-filter-toolbar__actions";
  const toggle = carbon("cds-button", "Filters") as HTMLElement;
  toggle.setAttribute("kind", "primary");
  toggle.setAttribute("size", "sm");
  const reset = carbon("cds-button", "Reset") as HTMLElement;
  reset.setAttribute("kind", "ghost");
  reset.setAttribute("size", "sm");
  actions.append(toggle, reset);
  toolbar.append(content, actions);

  const panel = document.createElement("div");
  panel.className = "filter-panel";
  panel.hidden = true;
  const controls = document.createElement("div");
  controls.className = "filter-grid";
  const optionControls = [
    optionSelect("company", "Company", data.options?.company ?? [], filters.company),
    optionSelect(
      "study_program",
      "Study program",
      data.options?.study_program ?? [],
      filters.study_program,
    ),
    optionSelect(
      "request_status",
      "Request status",
      data.options?.request_status ?? [],
      filters.request_status,
    ),
    optionSelect(
      "placement_type",
      "Placement type",
      data.options?.placement_type ?? [],
      filters.placement_type,
    ),
  ];
  optionControls.forEach(({ wrapper }) => controls.appendChild(wrapper));

  const datePicker = carbon("cds-date-picker") as HTMLElement & {
    value?: string;
  };
  datePicker.setAttribute("date-format", "Y-m-d");
  datePicker.setAttribute("value", `${filters.date_start}/${filters.date_end}`);
  const dateFrom = carbon("cds-date-picker-input") as HTMLElement;
  dateFrom.setAttribute("kind", "from");
  dateFrom.setAttribute("label-text", "Start date");
  const dateTo = carbon("cds-date-picker-input") as HTMLElement;
  dateTo.setAttribute("kind", "to");
  dateTo.setAttribute("label-text", "End date");
  datePicker.append(dateFrom, dateTo);
  controls.appendChild(datePicker);

  const apply = carbon("cds-button", "Apply filters") as HTMLElement;
  apply.setAttribute("kind", "primary");
  apply.setAttribute("size", "sm");
  panel.append(controls, apply);
  container.append(toolbar, panel);
  root.appendChild(container);

  const onToggle = () => {
    panel.hidden = !panel.hidden;
  };
  const onReset = () => emit(args, { type: "reset_filters" });
  const onApply = () => {
    const dateValues = (datePicker.value ?? "").split("/");
    const result: FilterValues = {
      date_start: dateValues[0] || filters.date_start,
      date_end: dateValues[1] || filters.date_end,
      company:
        (optionControls[0].select as HTMLElement & { value?: string }).value ??
        filters.company,
      study_program:
        (optionControls[1].select as HTMLElement & { value?: string }).value ??
        filters.study_program,
      request_status:
        (optionControls[2].select as HTMLElement & { value?: string }).value ??
        filters.request_status,
      placement_type:
        (optionControls[3].select as HTMLElement & { value?: string }).value ??
        filters.placement_type,
    };
    emit(args, { type: "apply_filters", filters: result });
    panel.hidden = true;
  };
  toggle.addEventListener("click", onToggle);
  reset.addEventListener("click", onReset);
  apply.addEventListener("click", onApply);

  return () => {
    toggle.removeEventListener("click", onToggle);
    reset.removeEventListener("click", onReset);
    apply.removeEventListener("click", onApply);
  };
};

const renderKpis = (root: HTMLElement, data: ComponentData) => {
  const grid = document.createElement("div");
  grid.className = "kpi-grid";
  (data.items ?? []).forEach((item) => {
    const tile = carbon("cds-tile") as HTMLElement;
    const label = document.createElement("span");
    label.className = "kpi-label";
    label.textContent = item.label;
    const value = document.createElement("strong");
    value.className = "kpi-value";
    value.textContent = item.value;
    tile.append(label, value);
    if (item.help) {
      const help = document.createElement("small");
      help.textContent = item.help;
      tile.appendChild(help);
    }
    grid.appendChild(tile);
  });
  root.appendChild(grid);
};

const formatStatusDate = (value?: string) => {
  const parts = (value ?? "").split("-").map(Number);
  if (
    parts.length !== 3 ||
    parts.some((part) => !Number.isInteger(part))
  ) {
    return "Unavailable";
  }
  return new Intl.DateTimeFormat("en-GB", {
    day: "numeric",
    month: "short",
    year: "numeric",
    timeZone: "UTC",
  }).format(new Date(Date.UTC(parts[0], parts[1] - 1, parts[2])));
};

const renderDataStatus = (
  root: HTMLElement,
  data: ComponentData,
  args: FrontendRendererArgs,
) => {
  const container = document.createElement("section");
  container.className = "cds-data-status";
  container.setAttribute("aria-label", "Data status");

  const summary = document.createElement("div");
  summary.className = "cds-data-status__summary";
  const meta = document.createElement("span");
  meta.className = "cds-data-status__meta";
  meta.textContent = `Updated ${formatStatusDate(data.as_of_date)} · ${(
    data.record_count ?? 0
  ).toLocaleString("en-US")} records`;

  const tags = document.createElement("div");
  tags.className = "cds-data-status__tags";
  const modeTag = carbon(
    "cds-tag",
    data.mode === "prototype" ? "Prototype data" : "Local data",
  ) as HTMLElement;
  modeTag.className = "cds-data-status__tag";
  modeTag.setAttribute("type", data.mode === "prototype" ? "cool-gray" : "blue");
  modeTag.setAttribute("size", "sm");
  tags.appendChild(modeTag);

  const kpiTag = carbon(
    "cds-tag",
    data.kpi_status === "validated"
      ? "Validated KPI logic"
      : "Provisional KPI logic",
  ) as HTMLElement;
  kpiTag.className = "cds-data-status__tag";
  kpiTag.setAttribute(
    "type",
    data.kpi_status === "validated" ? "green" : "yellow",
  );
  kpiTag.setAttribute("size", "sm");
  tags.appendChild(kpiTag);

  if ((data.warnings?.length ?? 0) > 0 && data.mode !== "prototype") {
    const warningTag = carbon("cds-tag", "Data warning") as HTMLElement;
    warningTag.className = "cds-data-status__tag";
    warningTag.setAttribute("type", "yellow");
    warningTag.setAttribute("size", "sm");
    tags.appendChild(warningTag);
  }

  const detailsId = `data-details-${args.key.replace(/[^a-zA-Z0-9_-]/g, "-")}`;
  const detailsToggle = carbon("cds-button", "Data details") as HTMLElement;
  detailsToggle.className = "cds-data-status__toggle";
  detailsToggle.setAttribute("kind", "ghost");
  detailsToggle.setAttribute("size", "sm");
  detailsToggle.setAttribute("aria-expanded", "false");
  detailsToggle.setAttribute("aria-controls", detailsId);
  summary.append(meta, tags, detailsToggle);

  const detailsPanel = document.createElement("div");
  detailsPanel.id = detailsId;
  detailsPanel.className = "cds-data-status__details";
  detailsPanel.hidden = true;
  const detailsList = document.createElement("dl");
  detailsList.className = "cds-data-status__detail-list";
  (data.detail_items ?? []).forEach((item) => {
    const detail = document.createElement("div");
    detail.className = "cds-data-status__detail";
    const label = document.createElement("dt");
    label.textContent = item.label;
    const value = document.createElement("dd");
    value.textContent = item.value;
    detail.append(label, value);
    detailsList.appendChild(detail);
  });

  const warningSection = document.createElement("div");
  warningSection.className = "cds-data-status__warnings";
  const warningTitle = document.createElement("strong");
  warningTitle.textContent = "Data contract warnings";
  warningSection.appendChild(warningTitle);
  if ((data.warnings ?? []).length) {
    const warningList = document.createElement("ul");
    (data.warnings ?? []).forEach((warning) => {
      const item = document.createElement("li");
      item.textContent = warning;
      warningList.appendChild(item);
    });
    warningSection.appendChild(warningList);
  } else {
    const noWarnings = document.createElement("p");
    noWarnings.textContent = "No data-contract warnings.";
    warningSection.appendChild(noWarnings);
  }
  detailsPanel.append(detailsList, warningSection);
  container.append(summary, detailsPanel);
  root.appendChild(container);

  const onToggle = () => {
    const expanded = detailsToggle.getAttribute("aria-expanded") === "true";
    detailsToggle.setAttribute("aria-expanded", String(!expanded));
    detailsPanel.hidden = expanded;
  };
  detailsToggle.addEventListener("click", onToggle);
  return () => detailsToggle.removeEventListener("click", onToggle);
};

const renderFeedback = (root: HTMLElement, data: ComponentData) => {
  const notification = carbon("cds-inline-notification") as HTMLElement;
  notification.setAttribute("kind", data.kind ?? "info");
  notification.setAttribute("low-contrast", "");
  notification.setAttribute("open", "");
  notification.setAttribute("title", data.title ?? "Information");
  notification.setAttribute("subtitle", data.subtitle ?? "");
  root.appendChild(notification);
};

const renderTable = (
  root: HTMLElement,
  data: ComponentData,
  args: FrontendRendererArgs,
) => {
  if (!(data.rows ?? []).length) {
    const empty = carbon("cds-tile");
    const emptyTitle = document.createElement("strong");
    emptyTitle.textContent = data.empty_title ?? "No records match";
    const emptyDetail = document.createElement("p");
    emptyDetail.textContent =
      data.empty_detail ?? "Adjust the active filters and try again.";
    empty.append(emptyTitle, emptyDetail);
    root.appendChild(empty);
    return;
  }

  const table = carbon("cds-table") as HTMLElement;
  const head = carbon("cds-table-head");
  const headerRow = carbon("cds-table-header-row");
  (data.columns ?? []).forEach((column) => {
    const cell = carbon("cds-table-header-cell", column.label);
    cell.setAttribute("data-key", column.key);
    headerRow.appendChild(cell);
  });
  head.appendChild(headerRow);

  const body = carbon("cds-table-body");
  (data.rows ?? []).forEach((row, index) => {
    const tableRow = carbon("cds-table-row") as HTMLElement;
    tableRow.dataset.row = String(index);
    (data.columns ?? []).forEach((column) => {
      tableRow.appendChild(
        carbon("cds-table-cell", String(row[column.key] ?? "—")),
      );
    });
    body.appendChild(tableRow);
  });
  table.append(head, body);
  root.appendChild(table);

  const pagination = carbon("cds-pagination") as HTMLElement;
  pagination.setAttribute("aria-label", "Table pagination");
  pagination.setAttribute("page", String(data.page ?? 1));
  pagination.setAttribute("page-size", String(data.page_size ?? 50));
  pagination.setAttribute("total-pages", String(data.total_pages ?? 1));
  pagination.setAttribute("total-items", String(data.total_rows ?? 0));
  pagination.setAttribute("start", String(data.row_offset ?? 0));
  pagination.setAttribute("page-size-input-disabled", "");
  pagination.setAttribute("items-per-page-text", "Rows per page");
  pagination.setAttribute("forward-text", "Next page");
  pagination.setAttribute("backward-text", "Previous page");
  pagination.className = "table-pagination";
  root.appendChild(pagination);

  const onRow = (event: Event) => {
    const row = (event.target as HTMLElement).closest<HTMLElement>("[data-row]")
      ?.dataset.row;
    if (row) emit(args, { type: "select_row", row: Number(row) });
  };
  const onPageChange = (event: Event) => {
    const detail = (event as CustomEvent<{ page?: number }>).detail;
    if (typeof detail?.page === "number") {
      emit(args, { type: "table_page", page: detail.page });
    }
  };
  body.addEventListener("click", onRow);
  pagination.addEventListener("cds-pagination-changed-current", onPageChange);
  return () => {
    body.removeEventListener("click", onRow);
    pagination.removeEventListener("cds-pagination-changed-current", onPageChange);
  };
};

const CarbonComponent: FrontendRenderer<Record<string, unknown>, ComponentData> = (
  args,
) => {
  const root = rootFor(args.parentElement);
  root.replaceChildren();
  switch (args.data.view) {
    case "shell":
      return renderShell(root, args.data, args);
    case "filters":
      return renderFilters(root, args.data, args);
    case "kpis":
      renderKpis(root, args.data);
      return;
    case "feedback":
      renderFeedback(root, args.data);
      return;
    case "data_status":
      return renderDataStatus(root, args.data, args);
    case "table":
      return renderTable(root, args.data, args);
  }
};

export default CarbonComponent;
