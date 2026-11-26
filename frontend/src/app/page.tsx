"use client";

import { FormEvent, useEffect, useState } from "react";

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const copy = {
  en: {
    dir: "ltr",
    brand: "FlowPilot AI",
    dashboard: "Dashboard",
    projects: "Projects",
    tasks: "Tasks",
    workflows: "Workflows",
    workspace: "Workspace",
    createWorkspace: "Create workspace",
    workspaceName: "Name your workspace",
    addTask: "Add task",
    taskTitle: "What needs to be done?",
    generate: "Generate workflow",
    prompt: "Describe your process...",
    overview: "Workspace overview",
    welcome: "Your ideas. Your workflows. Your control.",
    emptyTasks: "No tasks yet. Add one to get started.",
    liveStatus: "Workspace is ready",
    localActivity: "Workspace status",
    saveWorkflow: "Save draft",
    runWorkflow: "Run workflow",
    workflowCompleted: "Workflow completed",
    generatedDraft: "Template draft — review before saving",
    completed: "Completed",
    subtitle: "Plan the work, keep the team aligned, and make progress visible.",
    soon: "Soon",
    workspaceHint: "Choose a workspace to see its projects and activity.",
    taskHint: "Small steps make big work manageable.",
    workflowHint: "Turn a repeatable process into a simple, reviewable workflow.",
    templateNote: "Built-in guided templates — review each draft before saving.",
    noWorkspace: "Start with a workspace",
    noWorkspaceHint: "Create a workspace to organize projects, tasks, and workflows in one place.",
    projectName: "Project name",
    addProject: "Add project",
    emptyProjects: "No projects yet. Add one to organize your work.",
    emptyWorkflows: "No saved workflows yet.",
    about: "About",
    aboutTitle: "Bring everyday work into focus",
    aboutIntro: "Plan projects, keep tasks moving, and turn repeatable processes into clear, reviewable workflows—all from one multilingual workspace.",
    aboutWorkspacesTitle: "Organize workspaces and projects",
    aboutWorkspacesText: "Separate work by team or area, create focused projects, and keep each workspace’s tasks and workflows together.",
    aboutTasksTitle: "Track tasks from start to done",
    aboutTasksText: "Create project-linked tasks, choose priority, follow to-do and in-progress work, then complete or reopen items.",
    aboutWorkflowTitle: "Turn repeatable work into workflows",
    aboutWorkflowText: "Build and save multi-step task workflows, assign projects and priorities, add run-priority conditions, and set bounded retries. Review task-level outcomes and history after each run.",
    aboutOverviewTitle: "Make progress visible",
    aboutOverviewText: "See project and workflow totals, task counts, and completed work for the selected workspace.",
    aboutLanguagesTitle: "Choose your workspace language",
    aboutLanguagesText: "Use the interface in English, Urdu, or Arabic, with right-to-left layouts for Urdu and Arabic.",
    deploymentNoteTitle: "Before using real customer data",
    aboutDataNote: "Current deployment note: this build stores data in a local SQLite database and has no sign-in or team access controls. Before using sensitive customer data, deploy with authentication, authorization, backups, and a production database.",
    addStep: "Add task step",
    removeStep: "Remove",
    stepTitle: "Task description",
    priority: "Priority",
    retries: "Retries",
    condition: "Only run for priority",
    anyPriority: "Any priority",
    runPriority: "Run as",
    runHistory: "Run history",
    noRuns: "No runs recorded yet.",
    architecture: "Workflow architecture",
    createDraft: "Create workflow draft",
    saveChanges: "Save changes",
    newWorkflow: "New workflow",
    stepSkipped: "Skipped",
    stepFailed: "Failed",
    saveBeforeRun: "Save your changes before running this workflow.",
  },
  ur: {
    dir: "rtl",
    brand: "فلو پائلٹ AI",
    dashboard: "ڈیش بورڈ",
    projects: "پروجیکٹس",
    tasks: "کام",
    workflows: "ورک فلو",
    workspace: "ورک اسپیس",
    createWorkspace: "ورک اسپیس بنائیں",
    workspaceName: "ورک اسپیس کا نام",
    addTask: "کام شامل کریں",
    taskTitle: "کیا کام کرنا ہے؟",
    generate: "ورک فلو بنائیں",
    prompt: "اپنے عمل کے بارے میں لکھیں...",
    overview: "ورک اسپیس کا خلاصہ",
    welcome: "آپ کے خیالات۔ آپ کے ورک فلو۔ آپ کا کنٹرول۔",
    emptyTasks: "ابھی کوئی کام نہیں۔ شروع کرنے کے لیے ایک کام شامل کریں۔",
    liveStatus: "ورک اسپیس تیار ہے",
    localActivity: "ورک اسپیس کی حالت",
    saveWorkflow: "ڈرافٹ محفوظ کریں",
    runWorkflow: "ورک فلو چلائیں",
    workflowCompleted: "ورک فلو مکمل",
    generatedDraft: "ٹیمپلیٹ ڈرافٹ — محفوظ کرنے سے پہلے جائزہ لیں",
    completed: "مکمل",
    subtitle: "کام کی منصوبہ بندی کریں، ٹیم کو ساتھ رکھیں، اور پیش رفت دیکھیں۔",
    soon: "جلد",
    workspaceHint: "پروجیکٹس اور سرگرمی دیکھنے کے لیے ورک اسپیس منتخب کریں۔",
    taskHint: "چھوٹے قدم بڑے کام کو آسان بناتے ہیں۔",
    workflowHint: "دہرائے جانے والے عمل کو سادہ اور قابلِ جائزہ ورک فلو میں بدلیں۔",
    templateNote: "رہنمائی والے ٹیمپلیٹس — محفوظ کرنے سے پہلے ہر مرحلے کا جائزہ لیں۔",
    noWorkspace: "ورک اسپیس سے آغاز کریں",
    noWorkspaceHint: "پروجیکٹس، کام اور ورک فلو ایک جگہ منظم کرنے کے لیے ورک اسپیس بنائیں۔",
    projectName: "پروجیکٹ کا نام",
    addProject: "پروجیکٹ شامل کریں",
    emptyProjects: "ابھی کوئی پروجیکٹ نہیں۔ اپنا کام منظم کرنے کے لیے شامل کریں۔",
    emptyWorkflows: "ابھی کوئی محفوظ ورک فلو نہیں۔",
    about: "تعارف",
    aboutTitle: "روزمرہ کے کام کو واضح بنائیں",
    aboutIntro: "پروجیکٹس کی منصوبہ بندی کریں، کام کو آگے بڑھائیں اور دہرائے جانے والے عمل کو واضح، قابلِ جائزہ ورک فلو میں بدلیں — ایک کثیر لسانی ورک اسپیس میں۔",
    aboutWorkspacesTitle: "ورک اسپیس اور پروجیکٹس منظم کریں",
    aboutWorkspacesText: "ٹیم یا شعبے کے مطابق کام الگ رکھیں، واضح پروجیکٹس بنائیں، اور ہر ورک اسپیس کے کام اور ورک فلو اکٹھے رکھیں۔",
    aboutTasksTitle: "کام کو آغاز سے تکمیل تک دیکھیں",
    aboutTasksText: "پروجیکٹ سے منسلک کام بنائیں، ترجیح مقرر کریں، زیرِ عمل پیش رفت دیکھیں، پھر مکمل کریں یا دوبارہ کھولیں۔",
    aboutWorkflowTitle: "بار بار کے کام کو ورک فلو بنائیں",
    aboutWorkflowText: "کئی مراحل والے کام کے ورک فلو بنائیں اور محفوظ کریں، پروجیکٹس اور ترجیحات مقرر کریں، چلانے کی ترجیح کے قواعد اور محدود دوبارہ کوششیں شامل کریں۔ ہر رَن کے نتائج دیکھیں۔",
    aboutOverviewTitle: "پیش رفت واضح رکھیں",
    aboutOverviewText: "منتخب ورک اسپیس کے پروجیکٹس، ورک فلو، کام اور مکمل کاموں کی تعداد دیکھیں۔",
    aboutLanguagesTitle: "اپنی ورک اسپیس کی زبان منتخب کریں",
    aboutLanguagesText: "انگریزی، اردو یا عربی میں کام کریں، اردو اور عربی کے لیے دائیں سے بائیں لے آؤٹ کے ساتھ۔",
    deploymentNoteTitle: "حقیقی صارفین کا ڈیٹا استعمال کرنے سے پہلے",
    aboutDataNote: "موجودہ تعیناتی کی وضاحت: یہ ورژن ڈیٹا مقامی SQLite ڈیٹابیس میں رکھتا ہے اور اس میں سائن اِن یا ٹیم کی رسائی کا کنٹرول نہیں ہے۔ حساس صارفین کا ڈیٹا استعمال کرنے سے پہلے توثیق، اجازتوں، بیک اپ اور پروڈکشن ڈیٹابیس کے ساتھ تعینات کریں۔",
    addStep: "کام کا مرحلہ شامل کریں",
    removeStep: "ہٹائیں",
    stepTitle: "کام کی تفصیل",
    priority: "ترجیح",
    retries: "دوبارہ کوششیں",
    condition: "صرف اس ترجیح کے لیے چلائیں",
    anyPriority: "ہر ترجیح",
    runPriority: "چلانے کی ترجیح",
    runHistory: "چلانے کی تاریخ",
    noRuns: "ابھی کوئی رَن ریکارڈ نہیں۔",
    architecture: "ورک فلو کی ساخت",
    createDraft: "ورک فلو ڈرافٹ بنائیں",
    saveChanges: "تبدیلیاں محفوظ کریں",
    newWorkflow: "نیا ورک فلو",
    stepSkipped: "چھوڑ دیا گیا",
    stepFailed: "ناکام",
    saveBeforeRun: "ورک فلو چلانے سے پہلے تبدیلیاں محفوظ کریں۔",
  },
  ar: {
    dir: "rtl",
    brand: "فلو بايلوت AI",
    dashboard: "لوحة التحكم",
    projects: "المشاريع",
    tasks: "المهام",
    workflows: "سير العمل",
    workspace: "مساحة العمل",
    createWorkspace: "إنشاء مساحة عمل",
    workspaceName: "اسم مساحة العمل",
    addTask: "إضافة مهمة",
    taskTitle: "ما الذي يجب إنجازه؟",
    generate: "إنشاء سير عمل",
    prompt: "صف عمليتك...",
    overview: "نظرة عامة",
    welcome: "أفكارك. سير عملك. سيطرتك.",
    emptyTasks: "لا توجد مهام بعد. أضف مهمة للبدء.",
    liveStatus: "مساحة العمل جاهزة",
    localActivity: "حالة مساحة العمل",
    saveWorkflow: "حفظ المسودة",
    runWorkflow: "تشغيل سير العمل",
    workflowCompleted: "اكتمل سير العمل",
    generatedDraft: "مسودة قالب — راجعها قبل الحفظ",
    completed: "مكتمل",
    subtitle: "خطط للعمل، وأبقِ الفريق على اطلاع، واجعل التقدم واضحًا.",
    soon: "قريبًا",
    workspaceHint: "اختر مساحة عمل لعرض المشاريع والنشاط.",
    taskHint: "الخطوات الصغيرة تجعل الأعمال الكبيرة أسهل.",
    workflowHint: "حوّل العملية المتكررة إلى سير عمل بسيط قابل للمراجعة.",
    templateNote: "قوالب إرشادية — راجع كل خطوة قبل الحفظ والتنفيذ.",
    noWorkspace: "ابدأ بمساحة عمل",
    noWorkspaceHint: "أنشئ مساحة لتنظيم المشاريع والمهام وسير العمل في مكان واحد.",
    projectName: "اسم المشروع",
    addProject: "إضافة مشروع",
    emptyProjects: "لا توجد مشاريع بعد. أضف مشروعًا لتنظيم عملك.",
    emptyWorkflows: "لا يوجد سير عمل محفوظ بعد.",
    about: "عن المشروع",
    aboutTitle: "اجعل العمل اليومي أكثر وضوحًا",
    aboutIntro: "خطط للمشاريع، وتابع تقدم المهام، وحوّل الإجراءات المتكررة إلى مسارات عمل واضحة قابلة للمراجعة ضمن مساحة عمل متعددة اللغات.",
    aboutWorkspacesTitle: "تنظيم مساحات العمل والمشاريع",
    aboutWorkspacesText: "افصل العمل حسب الفريق أو المجال، وأنشئ مشاريع مركزة، واجمع مهام ومسارات كل مساحة عمل.",
    aboutTasksTitle: "متابعة المهام من البداية إلى الإنجاز",
    aboutTasksText: "أنشئ مهامًا مرتبطة بالمشاريع، وحدد الأولوية، وتابع العمل الجاري، ثم أكمل المهام أو أعد فتحها.",
    aboutWorkflowTitle: "تحويل الأعمال المتكررة إلى مسارات عمل",
    aboutWorkflowText: "أنشئ مسارات مهام متعددة الخطوات واحفظها، واربطها بالمشاريع وحدد الأولويات وشروط التشغيل وإعادات المحاولة المحدودة. راجع نتائج كل تشغيل.",
    aboutOverviewTitle: "اجعل التقدم واضحًا",
    aboutOverviewText: "اطّلع على أعداد المشاريع ومسارات العمل والمهام والمهام المكتملة في مساحة العمل المحددة.",
    aboutLanguagesTitle: "اختر لغة مساحة العمل",
    aboutLanguagesText: "استخدم الواجهة بالإنجليزية أو الأردية أو العربية، مع تخطيط من اليمين إلى اليسار للأردية والعربية.",
    deploymentNoteTitle: "قبل استخدام بيانات العملاء الحقيقية",
    aboutDataNote: "ملاحظة حول النشر الحالي: يخزن هذا الإصدار البيانات في قاعدة SQLite محلية ولا يتضمن تسجيل دخول أو ضوابط وصول للفريق. قبل استخدام بيانات عملاء حساسة، انشره مع المصادقة والتفويض والنسخ الاحتياطية وقاعدة بيانات إنتاجية.",
    addStep: "إضافة خطوة مهمة",
    removeStep: "إزالة",
    stepTitle: "وصف المهمة",
    priority: "الأولوية",
    retries: "إعادات المحاولة",
    condition: "التشغيل لهذه الأولوية فقط",
    anyPriority: "كل الأولويات",
    runPriority: "أولوية التشغيل",
    runHistory: "سجل التشغيل",
    noRuns: "لا توجد عمليات تشغيل مسجلة.",
    architecture: "معمارية سير العمل",
    createDraft: "إنشاء مسودة سير عمل",
    saveChanges: "حفظ التغييرات",
    newWorkflow: "سير عمل جديد",
    stepSkipped: "تم التخطي",
    stepFailed: "فشل",
    saveBeforeRun: "احفظ التغييرات قبل تشغيل سير العمل.",
  },
};

type Locale = keyof typeof copy;
type Workspace = { id: string; name: string; slug: string };
type Project = { id: string; name: string; description: string; status: "active" | "archived" };
type Task = { id: string; title: string; status: "todo" | "in_progress" | "done"; priority: string; project_id: string | null };
type WorkflowCondition = { field: "run_priority"; operator: "equals" | "not_equals"; value: "low" | "medium" | "high" };
type WorkflowStep = { id: string; action: "create_task"; title: string; priority: "low" | "medium" | "high"; project_id: string | null; max_retries: number; condition: WorkflowCondition | null };
type Workflow = { id: string; name: string; status: string; definition: string };
type WorkflowRun = { id: string; status: string; output: string; created_at: string };
type Stats = { projects: number; tasks: number; workflows: number; completed_tasks: number };

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API}${path}`, init);
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    const detail = typeof body?.detail === "string" ? body.detail : `Request failed (${response.status})`;
    throw new Error(detail);
  }
  return response.json() as Promise<T>;
}

function normalizeWorkflowStep(step: Partial<WorkflowStep>): WorkflowStep {
  return {
    id: step.id ?? crypto.randomUUID(),
    action: "create_task",
    title: step.title ?? "",
    priority: step.priority ?? "medium",
    project_id: step.project_id ?? null,
    max_retries: step.max_retries ?? 0,
    condition: step.condition ?? null,
  };
}

export default function Home() {
  const [locale, setLocale] = useState<Locale>("en");
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [workspace, setWorkspace] = useState<Workspace | null>(null);
  const [workspaceName, setWorkspaceName] = useState("");
  const [projects, setProjects] = useState<Project[]>([]);
  const [projectName, setProjectName] = useState("");
  const [tasks, setTasks] = useState<Task[]>([]);
  const [taskTitle, setTaskTitle] = useState("");
  const [taskProjectId, setTaskProjectId] = useState("");
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [activeSection, setActiveSection] = useState("dashboard");
  const [prompt, setPrompt] = useState("");
  const [draftName, setDraftName] = useState("");
  const [draft, setDraft] = useState<WorkflowStep[]>([]);
  const [savedWorkflow, setSavedWorkflow] = useState<Workflow | null>(null);
  const [workflowRuns, setWorkflowRuns] = useState<WorkflowRun[]>([]);
  const [workflowDirty, setWorkflowDirty] = useState(false);
  const [runPriority, setRunPriority] = useState<"low" | "medium" | "high">("medium");
  const [stats, setStats] = useState<Stats>({ projects: 0, tasks: 0, workflows: 0, completed_tasks: 0 });
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState("");
  const t = copy[locale];

  useEffect(() => {
    document.documentElement.lang = locale;
    document.documentElement.dir = t.dir;
  }, [locale, t.dir]);

  useEffect(() => {
    request<Workspace[]>("/api/v1/workspaces")
      .then((items) => {
        setWorkspaces(items);
        if (items.length > 0) setWorkspace((current) => current ?? items[0]);
      })
      .catch((error: Error) => setMessage(`Could not load workspaces: ${error.message}`));
  }, []);

  useEffect(() => {
    if (!workspace) return;
    let active = true;
    Promise.all([
      request<Project[]>(`/api/v1/projects?workspace_id=${encodeURIComponent(workspace.id)}`),
      request<Task[]>(`/api/v1/tasks?workspace_id=${encodeURIComponent(workspace.id)}`),
      request<Workflow[]>(`/api/v1/workflows?workspace_id=${encodeURIComponent(workspace.id)}`),
      request<Stats>(`/api/v1/analytics/overview?workspace_id=${encodeURIComponent(workspace.id)}`),
    ])
      .then(([projectData, taskData, workflowData, statData]) => {
        if (!active) return;
        setProjects(projectData);
        setTasks(taskData);
        setWorkflows(workflowData);
        setStats(statData);
      })
      .catch((error: Error) => {
        if (active) setMessage(`Could not load workspace data: ${error.message}`);
      });
    return () => { active = false; };
  }, [workspace]);

  async function createWorkspace() {
    const name = workspaceName.trim();
    if (name.length < 2) {
      setMessage("Enter a workspace name with at least 2 characters.");
      return;
    }
    setBusy("workspace");
    setMessage("");
    try {
      const item = await request<Workspace>("/api/v1/workspaces", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name }),
      });
      setWorkspaces((current) => [...current, item]);
      setWorkspace(item);
      setProjects([]);
      setTasks([]);
      setWorkflows([]);
      setStats({ projects: 0, tasks: 0, workflows: 0, completed_tasks: 0 });
      setWorkspaceName("");
      setMessage(`Workspace “${item.name}” created.`);
    } catch (error) {
      setMessage(`Could not create workspace: ${(error as Error).message}`);
    } finally {
      setBusy("");
    }
  }

  async function addProject(event: FormEvent) {
    event.preventDefault();
    if (!workspace || !projectName.trim()) return;
    setBusy("project");
    setMessage("");
    try {
      const item = await request<Project>("/api/v1/projects", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ workspace_id: workspace.id, name: projectName.trim(), description: "" }),
      });
      setProjects((current) => [...current, item]);
      setStats((current) => ({ ...current, projects: current.projects + 1 }));
      setProjectName("");
      setMessage("Project added.");
    } catch (error) {
      setMessage(`Could not add project: ${(error as Error).message}`);
    } finally {
      setBusy("");
    }
  }

  async function addTask(event: FormEvent) {
    event.preventDefault();
    if (!workspace || !taskTitle.trim()) return;
    setBusy("task");
    setMessage("");
    try {
      const item = await request<Task>("/api/v1/tasks", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ workspace_id: workspace.id, title: taskTitle.trim(), priority: "medium", project_id: taskProjectId || null }),
      });
      setTasks((current) => [...current, item]);
      setStats((current) => ({ ...current, tasks: current.tasks + 1 }));
      setTaskTitle("");
      setTaskProjectId("");
      setMessage("Task added.");
    } catch (error) {
      setMessage(`Could not add task: ${(error as Error).message}`);
    } finally {
      setBusy("");
    }
  }

  async function toggleTask(task: Task) {
    const status = task.status === "done" ? "todo" : "done";
    setMessage("");
    try {
      const updated = await request<Task>(`/api/v1/tasks/${task.id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status }),
      });
      setTasks((current) => current.map((item) => item.id === updated.id ? updated : item));
      setStats((current) => ({
        ...current,
        completed_tasks: current.completed_tasks + (status === "done" ? 1 : -1),
      }));
    } catch (error) {
      setMessage(`Could not update task: ${(error as Error).message}`);
    }
  }

  async function generate(event: FormEvent) {
    event.preventDefault();
    if (!prompt.trim()) return;
    setBusy("generate");
    setMessage("");
    setSavedWorkflow(null);
    try {
      const data = await request<{ name: string; steps: WorkflowStep[] }>("/api/v1/ai/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt }),
      });
      setDraftName(data.name ?? "Generated workflow");
      setDraft(data.steps);
      setMessage("Draft generated from built-in templates. Review each step before saving.");
    } catch (error) {
      setMessage(`Could not generate workflow: ${(error as Error).message}`);
    } finally {
      setBusy("");
    }
  }

  function addWorkflowStep() {
    setWorkflowDirty(true);
    setDraft((current) => [...current, {
      id: crypto.randomUUID(),
      action: "create_task",
      title: "",
      priority: "medium",
      project_id: null,
      max_retries: 0,
      condition: null,
    }]);
  }

  function updateWorkflowStep(index: number, patch: Partial<WorkflowStep>) {
    setWorkflowDirty(true);
    setDraft((current) => current.map((step, stepIndex) => stepIndex === index ? { ...step, ...patch } : step));
  }

  async function selectWorkflow(workflow: Workflow) {
    try {
      const definition = JSON.parse(workflow.definition) as { steps: Partial<WorkflowStep>[] };
      setSavedWorkflow(workflow);
      setDraftName(workflow.name);
      setDraft(definition.steps.map(normalizeWorkflowStep));
      setWorkflowDirty(false);
      setMessage("");
      setWorkflowRuns(await request<WorkflowRun[]>(`/api/v1/workflows/${workflow.id}/runs`));
    } catch (error) {
      setMessage(`Could not load workflow: ${(error as Error).message}`);
    }
  }

  function startNewWorkflow() {
    setSavedWorkflow(null);
    setWorkflowRuns([]);
    setWorkflowDirty(false);
    setDraftName("");
    setDraft([]);
    setMessage("");
  }

  async function saveWorkflow() {
    if (!workspace || draft.length === 0) return;
    setBusy("save");
    setMessage("");
    try {
      const item = await request<Workflow>(savedWorkflow ? `/api/v1/workflows/${savedWorkflow.id}` : "/api/v1/workflows", {
        method: savedWorkflow ? "PATCH" : "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(savedWorkflow
          ? { name: draftName || "Workflow", steps: draft }
          : { workspace_id: workspace.id, name: draftName || "Generated workflow", steps: draft }),
      });
      setSavedWorkflow(item);
      setWorkflowDirty(false);
      setWorkflows((current) => current.some((workflow) => workflow.id === item.id)
        ? current.map((workflow) => workflow.id === item.id ? item : workflow)
        : [...current, item]);
      if (!savedWorkflow) setStats((current) => ({ ...current, workflows: current.workflows + 1 }));
      setMessage(savedWorkflow ? "Workflow changes saved." : "Workflow saved. Review and run it when ready.");
    } catch (error) {
      setMessage(`Could not save workflow: ${(error as Error).message}`);
    } finally {
      setBusy("");
    }
  }

  async function runWorkflow() {
    if (!savedWorkflow || !window.confirm("Run this workflow now? Matching steps will create tasks in the selected workspace.")) return;
    setBusy("run");
    setMessage("");
    try {
      const run = await request<WorkflowRun>(`/api/v1/workflows/${savedWorkflow.id}/run`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ priority: runPriority }),
      });
      setWorkflowRuns((current) => [run, ...current]);
      const [taskData, statData] = await Promise.all([
        request<Task[]>(`/api/v1/tasks?workspace_id=${encodeURIComponent(workspace!.id)}`),
        request<Stats>(`/api/v1/analytics/overview?workspace_id=${encodeURIComponent(workspace!.id)}`),
      ]);
      setTasks(taskData);
      setStats(statData);
      setMessage(run.status === "succeeded" ? "Workflow run completed. Results are in the run history." : "Workflow run failed. Review the run history for step results.");
    } catch (error) {
      setMessage(`Could not run workflow: ${(error as Error).message}`);
    } finally {
      setBusy("");
    }
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand"><span className="brand-mark">F</span>{t.brand}</div>
        <nav aria-label="Primary navigation">
          {[
            { id: "dashboard", icon: "⌂", label: t.dashboard },
            { id: "projects", icon: "◇", label: t.projects },
            { id: "tasks", icon: "✓", label: t.tasks },
            { id: "workflows", icon: "↯", label: t.workflows },
            { id: "about", icon: "ⓘ", label: t.about },
          ].map((item) => (
            <button
              key={item.id}
              className={`nav-item ${activeSection === item.id ? "active" : ""}`}
              aria-current={activeSection === item.id ? "page" : undefined}
              onClick={() => {
                setActiveSection(item.id);
                document.getElementById(item.id)?.scrollIntoView({ behavior: "smooth", block: "start" });
              }}
            >
              <span className="nav-icon" aria-hidden="true">{item.icon}</span><span>{item.label}</span>
            </button>
          ))}
        </nav>
        <div className="language-picker" aria-label="Language">
          {(["en", "ur", "ar"] as Locale[]).map((value) => (
            <button key={value} className={locale === value ? "selected" : ""} aria-pressed={locale === value} onClick={() => setLocale(value)}>{value.toUpperCase()}</button>
          ))}
        </div>
      </aside>

      <main className="main">
        <header className="topbar">
          <div className="hero-copy"><p className="eyebrow">{t.overview}</p><h1>{t.welcome}</h1><p className="hero-subtitle">{t.subtitle}</p></div>
          <div className="header-actions">
            <div className="workspace-status"><span className="status-dot" /><div><small>{t.localActivity}</small><strong>{workspace ? t.liveStatus : t.noWorkspace}</strong></div></div>
            <div className="workspace-create">
              <input aria-label={t.workspaceName} value={workspaceName} onChange={(event) => setWorkspaceName(event.target.value)} placeholder={t.workspaceName} maxLength={100} />
              <button className="primary" onClick={createWorkspace} disabled={busy === "workspace"}>+ {t.createWorkspace}</button>
            </div>
          </div>
        </header>

        {message && <div className="feedback" role="status">{message}<button aria-label="Dismiss message" onClick={() => setMessage("")}>×</button></div>}

        <section className={`workspace-row ${workspace ? "" : "workspace-unselected"}`}>
          <div className="workspace-label"><label htmlFor="workspace-select">{t.workspace}</label>{!workspace && <span>{t.workspaceHint}</span>}</div>
          <select id="workspace-select" value={workspace?.id ?? ""} onChange={(event) => {
            setWorkspace(workspaces.find((item) => item.id === event.target.value) ?? null);
            setProjects([]);
            setTasks([]);
            setWorkflows([]);
            setStats({ projects: 0, tasks: 0, workflows: 0, completed_tasks: 0 });
            setDraft([]);
            setDraftName("");
            setSavedWorkflow(null);
            setWorkflowRuns([]);
            setWorkflowDirty(false);
          }}>
            <option value="">Select workspace</option>
            {workspaces.map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}
          </select>
        </section>

        <section className="stats-grid" id="dashboard" aria-label="Workspace statistics">
          {[
            { label: t.projects, value: stats.projects },
            { label: t.tasks, value: stats.tasks },
            { label: t.workflows, value: stats.workflows },
            { label: t.completed, value: stats.completed_tasks },
          ].map((card, index) => <article className={`stat-card stat-card-${index + 1}`} key={card.label}><span className="stat-icon" aria-hidden="true">{["◇", "✓", "↯", "✦"][index]}</span><div><span className="stat-label">{card.label}</span><strong>{card.value}</strong></div></article>)}
        </section>

        <section className="content-grid">
          <article className="panel" id="projects">
            <div className="panel-heading"><div><h2>{t.projects}</h2><p>{t.workspaceHint}</p></div><span className="panel-count">{projects.length}</span></div>
            <form onSubmit={addProject} className="task-form">
              <input aria-label={t.projectName} value={projectName} onChange={(event) => setProjectName(event.target.value)} placeholder={t.projectName} maxLength={100} disabled={!workspace} />
              <button className="small-button" type="submit" disabled={!workspace || !projectName.trim() || busy === "project"}>+ {t.addProject}</button>
            </form>
            <div className="project-list">
              {!workspace ? <p className="empty">{t.noWorkspaceHint}</p> : projects.length === 0 ? <p className="empty">{t.emptyProjects}</p> : projects.map((project) => (
                <div className="project-row" key={project.id}><span className="project-symbol">◇</span><div><strong>{project.name}</strong><small>{project.status}</small></div></div>
              ))}
            </div>
          </article>

          <article className="panel" id="tasks">
            <div className="panel-heading"><div><h2>{t.tasks}</h2><p>{t.taskHint}</p></div><span className="panel-count">{tasks.length}</span></div>
            <form onSubmit={addTask} className="task-form task-form-full">
              <input aria-label={t.taskTitle} value={taskTitle} onChange={(event) => setTaskTitle(event.target.value)} placeholder={t.taskTitle} maxLength={200} disabled={!workspace} />
              <select aria-label="Project" value={taskProjectId} onChange={(event) => setTaskProjectId(event.target.value)} disabled={!workspace || projects.length === 0}>
                <option value="">No project</option>
                {projects.map((project) => <option key={project.id} value={project.id}>{project.name}</option>)}
              </select>
              <button className="small-button" type="submit" disabled={!workspace || !taskTitle.trim() || busy === "task"}>+ {t.addTask}</button>
            </form>
            <div className="task-list">
              {!workspace ? <p className="empty">{t.noWorkspaceHint}</p> : tasks.length === 0 ? <p className="empty">{t.emptyTasks}</p> : tasks.map((task) => (
                <div className={`task-row ${task.status === "done" ? "task-done" : ""}`} key={task.id}>
                  <button className="task-check" aria-label={task.status === "done" ? `Reopen ${task.title}` : `Complete ${task.title}`} aria-pressed={task.status === "done"} onClick={() => toggleTask(task)} />
                  <div><strong>{task.title}</strong><small>{task.priority}</small></div>
                  <span className="status">{task.status.replace("_", " ")}</span>
                </div>
              ))}
            </div>
          </article>

          <article className="panel workflow-panel" id="workflows">
            <div className="panel-heading"><div><h2>{t.workflows}</h2><p>{t.workflowHint}</p></div><span className="panel-symbol" aria-hidden="true">↯</span></div>
            <div className="workflow-toolbar">
              <button className="small-button" onClick={() => { startNewWorkflow(); setDraftName("New workflow"); addWorkflowStep(); }}>{t.newWorkflow}</button>
              <form onSubmit={generate} className="workflow-form workflow-generate">
                <textarea value={prompt} onChange={(event) => setPrompt(event.target.value)} placeholder={t.prompt} maxLength={1000} />
                <small>{t.templateNote}</small>
                <button className="primary" type="submit" disabled={!prompt.trim() || busy === "generate"}>↯ {t.generate}</button>
              </form>
            </div>
            <div className="saved-workflows">
              {workflows.map((workflow) => (
                <button key={workflow.id} className={`saved-workflow ${savedWorkflow?.id === workflow.id ? "selected" : ""}`} onClick={() => void selectWorkflow(workflow)}>
                  <span>↯</span><strong>{workflow.name}</strong><small>{workflow.status}</small>
                </button>
              ))}
              {workflows.length === 0 && <p className="empty compact-empty">{t.emptyWorkflows}</p>}
            </div>

            <h3 className="diagram-title">{t.architecture}</h3>
            <div className="flow-diagram" role="img" aria-label="Workflow path: review draft, evaluate conditions, run task steps with retries, and save run history">
              <div><span>01</span><strong>Review draft</strong><small>Validated steps</small></div>
              <i aria-hidden="true">→</i>
              <div><span>02</span><strong>Condition gate</strong><small>Match run priority</small></div>
              <i aria-hidden="true">→</i>
              <div><span>03</span><strong>Execute tasks</strong><small>Bounded retries</small></div>
              <i aria-hidden="true">→</i>
              <div><span>04</span><strong>Run history</strong><small>Per-step results</small></div>
            </div>

            {draft.length > 0 && (
              <div className="draft workflow-editor">
                <label className="workflow-name-field"><span>{t.workflows}</span><input value={draftName} onChange={(event) => { setDraftName(event.target.value); setWorkflowDirty(true); }} maxLength={100} /></label>
                <span>{t.generatedDraft}</span>
                {draft.map((step, index) => (
                  <div className="workflow-step-editor" key={step.id}>
                    <div className="step-editor-heading"><strong>Step {index + 1}</strong><button type="button" className="text-button" onClick={() => { setWorkflowDirty(true); setDraft((current) => current.filter((_, stepIndex) => stepIndex !== index)); }}>{t.removeStep}</button></div>
                    <input aria-label={t.stepTitle} value={step.title} onChange={(event) => updateWorkflowStep(index, { title: event.target.value })} maxLength={200} placeholder={t.stepTitle} />
                    <div className="step-options">
                      <label>{t.priority}
                        <select value={step.priority ?? "medium"} onChange={(event) => updateWorkflowStep(index, { priority: event.target.value as WorkflowStep["priority"] })}>
                          <option value="low">Low</option><option value="medium">Medium</option><option value="high">High</option>
                        </select>
                      </label>
                      <label>{t.retries}
                        <select value={step.max_retries ?? 0} onChange={(event) => updateWorkflowStep(index, { max_retries: Number(event.target.value) })}>
                          <option value={0}>0</option><option value={1}>1</option><option value={2}>2</option><option value={3}>3</option>
                        </select>
                      </label>
                      <label>{t.condition}
                        <select value={step.condition?.value ?? ""} onChange={(event) => updateWorkflowStep(index, { condition: event.target.value ? { field: "run_priority", operator: "equals", value: event.target.value as WorkflowStep["priority"] } : null })}>
                          <option value="">{t.anyPriority}</option><option value="low">Low</option><option value="medium">Medium</option><option value="high">High</option>
                        </select>
                      </label>
                      <label>Project
                        <select value={step.project_id ?? ""} onChange={(event) => updateWorkflowStep(index, { project_id: event.target.value || null })}>
                          <option value="">No project</option>
                          {projects.map((project) => <option key={project.id} value={project.id}>{project.name}</option>)}
                        </select>
                      </label>
                    </div>
                  </div>
                ))}
                <div className="workflow-actions">
                  <button className="small-button secondary-button" onClick={addWorkflowStep}>{t.addStep}</button>
                  <button className="small-button" disabled={!workspace || busy === "save" || draft.some((step) => !step.title.trim())} onClick={saveWorkflow}>{savedWorkflow ? t.saveChanges : t.saveWorkflow}</button>
                </div>
                {savedWorkflow && (
                  <div className="run-controls">
                    <label>{t.runPriority}
                      <select value={runPriority} onChange={(event) => setRunPriority(event.target.value as typeof runPriority)}>
                        <option value="low">Low</option><option value="medium">Medium</option><option value="high">High</option>
                      </select>
                    </label>
                    <button className="primary" disabled={busy === "run" || workflowDirty} onClick={runWorkflow}>{busy === "run" ? "Running..." : t.runWorkflow}</button>
                  </div>
                )}
                {workflowDirty && savedWorkflow && <small>{t.saveBeforeRun}</small>}
              </div>
            )}

            {savedWorkflow && (
              <section className="run-history">
                <h3>{t.runHistory}</h3>
                {workflowRuns.length === 0 ? <p>{t.noRuns}</p> : workflowRuns.map((run) => (
                  <details className="run-record" key={run.id}>
                    <summary><span className={`run-state run-${run.status}`}>{run.status}</span><time>{new Date(run.created_at).toLocaleString()}</time></summary>
                    <pre>{run.output}</pre>
                  </details>
                ))}
              </section>
            )}
          </article>
        </section>

        <section className="about-section" id="about">
          <div className="about-heading">
            <p className="eyebrow">{t.about}</p>
            <h2>{t.aboutTitle}</h2>
            <p>{t.aboutIntro}</p>
          </div>
          <div className="about-grid">
            {[
              { icon: "◇", title: t.aboutWorkspacesTitle, text: t.aboutWorkspacesText },
              { icon: "✓", title: t.aboutTasksTitle, text: t.aboutTasksText },
              { icon: "↯", title: t.aboutWorkflowTitle, text: t.aboutWorkflowText },
              { icon: "▥", title: t.aboutOverviewTitle, text: t.aboutOverviewText },
              { icon: "文", title: t.aboutLanguagesTitle, text: t.aboutLanguagesText },
            ].map((feature) => (
              <article className="about-card" key={feature.title}>
                <span className="about-icon" aria-hidden="true">{feature.icon}</span>
                <h3>{feature.title}</h3>
                <p>{feature.text}</p>
              </article>
            ))}
          </div>
          <p className="about-data-note"><strong>{t.deploymentNoteTitle}:</strong> {t.aboutDataNote}</p>
        </section>
      </main>
    </div>
  );
}
