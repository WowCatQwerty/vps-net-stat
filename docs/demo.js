/* ============================================================
   vps-net-stat — interactive demo menu
   Fully client-side fake engine. Nothing is sent anywhere,
   state lives in this browser's localStorage only.
   ============================================================ */

(() => {
  "use strict";

  const STORAGE_KEY = "vns_demo_state_v2";
  const DEMO_VERSION_INSTALLED = "4.4.3";   // version "already installed" on first visit
  const DEMO_VERSION_LATEST    = "4.4.4";   // version you can "update" to

  const $body = document.getElementById("termBody");
  const $hint = document.getElementById("termHint");
  const $brandTag = document.getElementById("brandTag");
  const $langBtn = document.getElementById("langBtn");
  const $resetBtn = document.getElementById("resetBtn");

  // ── i18n ────────────────────────────────────────────────────────────────
  const STRINGS = {
    en: {
      brandTag: "— interactive demo menu",
      hintOpen: "Type {vns} and press {Enter} to open the menu",
      hintHistory: "{↑}/{↓} command history",
      resetBtn: "↺ reset",
      resetConfirm: "Reset the demo to a fresh install state? All fake traffic and settings will be lost.",
      welcome: "Welcome to the vps-net-stat demo.",
      notInstalled: "The program isn't \"installed\" in this session yet.",
      typeInstall: "Type:  install.sh",
      alreadyInstalled: "vps-net-stat is already \"installed\" — as if you came back to your own server.",
      typeVns: "Type:  vns",
      helpHint: "Hint: help — list of available demo commands.",
      bashNotFound: (c) => `bash: ${c}: command not found`,
      vnsNotFound: [
        "bash: vns: command not found",
        "vps-net-stat is not installed. Run:",
      ],
      installCmdHint: "curl -fsSL https://raw.githubusercontent.com/WowCatQwerty/vps-net-stat/main/install.sh | sudo bash",
      helpTitle: "Available demo commands:",
      helpVns: "open the interactive menu",
      helpClear: "clear the screen",
      helpHelp: "this help text",
      helpInstall: "install vps-net-stat (demo)",
      unknownCmd: (c) => `bash: ${c}: command not found. Type help.`,
      installing: [
        "→ Checking dependencies…",
        "✓ Checking dependencies…",
        "→ Downloading files from GitHub…",
        "✓ Downloading files from GitHub…",
        "→ Installing systemd service…",
        "✓ Installing systemd service…",
      ],
      installDone: (v) => `✓ vps-net-stat installed successfully! (version ${v})`,
      installHint: "Type vns to open the menu.",
      menuTitle: "vps-net-stat — VPS Network Monitor",
      version: "Version:",
      newVersion: "🟢 New version available:",
      diskUsage: "Disk usage:",
      diskDb: "database",
      diskApp: "app",
      monthlyLimit: "Monthly limit:",
      chooseAction: "Choose an action:",
      choosePrompt: "Enter a menu number and press Enter.",
      unknownMenuItem: "Unknown menu item.",
      pressEnter: "Press Enter to return to menu…",
      menuClosed: "Menu closed.",
      items: [
        ["1","Summary (today / month / all time)"],
        ["2","Open ports with processes"],
        ["3","Traffic by all months"],
        ["4","Traffic for last N days"],
        ["5","Top ports by traffic"],
        ["6","Traffic charts"],
        ["─",null],
        ["7","Add port for traffic tracking"],
        ["8","Remove port from tracking"],
        ["9","Watched ports"],
        ["─",null],
        ["10","Reset server traffic stats"],
        ["11","Reset port traffic stats"],
        ["12","Export / Import statistics"],
        ["13","Set monthly traffic limit"],
        ["─",null],
        ["14","System info"],
        ["15","Diagnostics"],
        ["─",null],
        ["16","Uninstall"],
        ["17","Update vps-net-stat"],
        ["18","Restart service"],
        ["19","Switch language (Переключить на Русский)"],
        ["0","Exit"],
      ],
      summaryTitle: "vps-net-stat — summary",
      period: "Period", incoming: "↓ Incoming", outgoing: "↑ Outgoing",
      today: "Today", month: "Month", allTime: "All time",
      openPorts: "Open ports:",
      portsHeader: (t) => `Open ports (scanned at: ${t})`,
      portsTotal: "Total ports:",
      allMonthsTitle: "Traffic by all months",
      noData: "No data yet.",
      monthCol: "Month", total: "Total",
      grandTotal: "Grand total",
      daysTitle: (n) => `Traffic for last ${n} days`,
      dayCol: "Day",
      dailyTotal: "Total",
      portTopTitle: "Top ports by traffic — All time",
      portTopEmpty: "No data yet. Add a port to tracking (menu item 7).",
      portCol: "Port", protoCol: "Protocol", commentCol: "Comment", addedCol: "Added",
      chartsTitle: (n) => `Traffic for last ${n} days`,
      chartsEmpty: "No data for chart",
      chartsIncoming: "Incoming", chartsOutgoing: "Outgoing",
      chartsTotal: "Total:",
      watchedTitle: "Watched ports",
      watchedEmpty: "No watched ports. Add one via menu item [7].",
      infoTitle: "vps-net-stat — info",
      svcRunning: "Service: running",
      uptime: "Service uptime:",
      lastScan: "Last scan:",
      secAgo: "sec ago",
      tracked: "Tracked ports:",
      backend: "Port traffic backend:",
      backendVal: "nftables (exact)",
      doctorTitle: "vps-net-stat — diagnostics",
      doctorChecks: [
        "systemd service running",
        "SQLite database accessible",
        "/proc/net/dev readable",
        "ss installed",
        "ip installed",
        "Interface detected: eth0",
        "Write access to data directory",
      ],
      doctorDisk: (v) => `Free disk space: ${v}`,
      doctorFresh: "Database updated recently",
      doctorAllOk: "✓ Everything looks good",
      resetServerDone: "Server traffic data deleted.",
      resetServerConfirm: "Delete all server traffic data? [y/N]: ",
      resetPortConfirm: (p) => `Delete traffic for port ${p}? [y/N]: `,
      resetPortDone: (p) => `Traffic for port ${p} deleted.`,
      cancelled: "Cancelled.",
      invalidPort: "Invalid port number.",
      portPrompt: "Port number (e.g. 80): ",
      protoPrompt: "Protocol: [1] tcp  [2] udp  [3] both",
      protoArrow: "→ ",
      commentPrompt: "Comment (optional): ",
      portAdded: "Port added to tracking.",
      portAlready: "This port is already being tracked.",
      portDelPrompt: "Port number to remove: ",
      portRemoved: "Port removed from tracking.",
      portNotFound: "Port not found in list.",
      exportImportUnavailable: "Export/Import isn't available in the browser demo — in the real program, data is saved to the server's disk.",
      limitCurrent: (v) => `Current limit: ${v}`,
      limitNone: "not set",
      limitPrompt: "Monthly limit GiB (0 = disable): ",
      limitSet: (v) => `Limit set: ${v} GiB`,
      limitDisabled: "Limit disabled.",
      limitInvalid: "Invalid value.",
      resetPortNumberPrompt: "Port number: ",
      alreadyLatest: (v) => `Version ${v} is already up to date. No update needed.`,
      updating: (from,to) => `Update: ${from} → ${to}`,
      updateSteps: [
        "→ Downloading vps-net-stat.py…",
        "→ Downloading vns.py…",
        "→ Downloading vps-net-stat.service…",
        "→ Downloading version.txt…",
        "✓ Files downloaded",
        "→ Verifying file integrity (SHA-256)…",
        "✓ File integrity confirmed",
        "→ Installing files…",
        "✓ Files updated",
        "→ Restarting service…",
        "✓ Service restarted",
      ],
      updateDone: (v) => `✓ Updated to v${v} successfully! Data preserved.`,
      restarting: "→ Restarting service…",
      restarted: "✓ Service restarted.",
      uninstallConfirm: "Uninstall vps-net-stat? [y/N]: ",
      uninstalled: "Program uninstalled.",
      uninstalledDbNote: "Database was not preserved (demo mode).",
      reinstallHint: "To start over — type install.sh or click \"↺ reset\".",
      langSwitched: "Language switched.",
    },
    ru: {
      brandTag: "— интерактивное демо меню",
      hintOpen: "Введите {vns} и нажмите {Enter}, чтобы открыть меню",
      hintHistory: "{↑}/{↓} история команд",
      resetBtn: "↺ сброс",
      resetConfirm: "Сбросить демо к состоянию новой установки? Весь фейковый трафик и настройки будут потеряны.",
      welcome: "Добро пожаловать в демо vps-net-stat.",
      notInstalled: "Программа пока не установлена в этой сессии.",
      typeInstall: "Наберите:  install.sh",
      alreadyInstalled: "vps-net-stat уже «установлен» — как будто вы вернулись на свой сервер.",
      typeVns: "Наберите:  vns",
      helpHint: "Подсказка: help — список доступных демо-команд.",
      bashNotFound: (c) => `bash: ${c}: команда не найдена`,
      vnsNotFound: [
        "bash: vns: команда не найдена",
        "vps-net-stat не установлен. Запустите:",
      ],
      installCmdHint: "curl -fsSL https://raw.githubusercontent.com/WowCatQwerty/vps-net-stat/main/install.sh | sudo bash",
      helpTitle: "Доступные команды демо:",
      helpVns: "открыть интерактивное меню",
      helpClear: "очистить экран",
      helpHelp: "эта справка",
      helpInstall: "установить vps-net-stat (демо)",
      unknownCmd: (c) => `bash: ${c}: команда не найдена. Наберите help.`,
      installing: [
        "→ Проверяю зависимости…",
        "✓ Проверяю зависимости…",
        "→ Скачиваю файлы из GitHub…",
        "✓ Скачиваю файлы из GitHub…",
        "→ Устанавливаю systemd-сервис…",
        "✓ Устанавливаю systemd-сервис…",
      ],
      installDone: (v) => `✓ vps-net-stat успешно установлен! (версия ${v})`,
      installHint: "Наберите vns, чтобы открыть меню.",
      menuTitle: "vps-net-stat — Мониторинг сети VPS",
      version: "Версия:",
      newVersion: "🟢 Доступна новая версия:",
      diskUsage: "Размер на диске:",
      diskDb: "база",
      diskApp: "программа",
      monthlyLimit: "Месячный лимит:",
      chooseAction: "Выберите действие:",
      choosePrompt: "Введите номер пункта меню и нажмите Enter.",
      unknownMenuItem: "Неизвестный пункт меню.",
      pressEnter: "Нажмите Enter для возврата в меню…",
      menuClosed: "Меню закрыто.",
      items: [
        ["1","Сводка (сегодня / месяц / всего)"],
        ["2","Открытые порты с процессами"],
        ["3","Трафик по всем месяцам"],
        ["4","Трафик за последние N дней"],
        ["5","Топ портов по трафику"],
        ["6","Графики трафика"],
        ["─",null],
        ["7","Добавить порт для отслеживания трафика"],
        ["8","Убрать порт из отслеживания"],
        ["9","Отслеживаемые порты"],
        ["─",null],
        ["10","Сбросить трафик сервера"],
        ["11","Сбросить трафик порта"],
        ["12","Экспорт / Импорт статистики"],
        ["13","Настроить месячный лимит трафика"],
        ["─",null],
        ["14","Информация о системе"],
        ["15","Диагностика"],
        ["─",null],
        ["16","Удалить программу"],
        ["17","Обновить vps-net-stat"],
        ["18","Перезапустить сервис"],
        ["19","Switch language (переключить на английский)"],
        ["0","Выйти"],
      ],
      summaryTitle: "vps-net-stat — сводка",
      period: "Период", incoming: "↓ Входящий", outgoing: "↑ Исходящий",
      today: "Сегодня", month: "Месяц", allTime: "Всё время",
      openPorts: "Открытых портов:",
      portsHeader: (t) => `Открытые порты (снято: ${t})`,
      portsTotal: "Итого портов:",
      allMonthsTitle: "Трафик по всем месяцам",
      noData: "Нет данных.",
      monthCol: "Месяц", total: "Всего",
      grandTotal: "Всего",
      daysTitle: (n) => `Трафик за последние ${n} дней`,
      dayCol: "День",
      dailyTotal: "Итого",
      portTopTitle: "Топ портов по трафику — Всё время",
      portTopEmpty: "Нет данных. Добавьте порт в отслеживание (пункт 7).",
      portCol: "Порт", protoCol: "Протокол", commentCol: "Комментарий", addedCol: "Добавлен",
      chartsTitle: (n) => `Трафик за последние ${n} дней`,
      chartsEmpty: "Нет данных для графика",
      chartsIncoming: "Входящий", chartsOutgoing: "Исходящий",
      chartsTotal: "Итого:",
      watchedTitle: "Отслеживаемые порты",
      watchedEmpty: "Нет отслеживаемых портов. Добавьте через пункт меню [7].",
      infoTitle: "vps-net-stat — информация",
      svcRunning: "Сервис: запущен",
      uptime: "Время работы сервиса:",
      lastScan: "Последнее сканирование:",
      secAgo: "сек назад",
      tracked: "Отслеживаемых портов:",
      backend: "Учёт трафика по портам:",
      backendVal: "nftables (точно)",
      doctorTitle: "vps-net-stat — диагностика",
      doctorChecks: [
        "systemd сервис запущен",
        "SQLite база доступна",
        "/proc/net/dev читается",
        "ss установлен",
        "ip установлен",
        "Интерфейс обнаружен: eth0",
        "Права на запись в директории данных",
      ],
      doctorDisk: (v) => `Свободно на диске: ${v}`,
      doctorFresh: "База обновлялась недавно",
      doctorAllOk: "✓ Всё в порядке",
      resetServerDone: "Трафик сервера удалён.",
      resetServerConfirm: "Удалить весь трафик сервера? [y/N]: ",
      resetPortConfirm: (p) => `Удалить трафик порта ${p}? [y/N]: `,
      resetPortDone: (p) => `Трафик порта ${p} удалён.`,
      cancelled: "Отмена.",
      invalidPort: "Некорректный номер порта.",
      portPrompt: "Номер порта (например 80): ",
      protoPrompt: "Протокол: [1] tcp  [2] udp  [3] оба",
      protoArrow: "→ ",
      commentPrompt: "Комментарий (необязательно): ",
      portAdded: "Порт добавлен в отслеживание.",
      portAlready: "Этот порт уже отслеживается.",
      portDelPrompt: "Номер порта для удаления: ",
      portRemoved: "Порт убран из отслеживания.",
      portNotFound: "Порт не найден в списке.",
      exportImportUnavailable: "Экспорт/Импорт недоступны в браузерном демо — в реальной программе данные сохраняются на диск сервера.",
      limitCurrent: (v) => `Текущий лимит: ${v}`,
      limitNone: "не установлен",
      limitPrompt: "Месячный лимит ГиБ (0 = отключить): ",
      limitSet: (v) => `Лимит установлен: ${v} GiB`,
      limitDisabled: "Лимит отключён.",
      limitInvalid: "Некорректное значение.",
      resetPortNumberPrompt: "Номер порта: ",
      alreadyLatest: (v) => `Версия ${v} уже актуальна. Обновление не требуется.`,
      updating: (from,to) => `Обновление: ${from} → ${to}`,
      updateSteps: [
        "→ Скачиваю vps-net-stat.py…",
        "→ Скачиваю vns.py…",
        "→ Скачиваю vps-net-stat.service…",
        "→ Скачиваю version.txt…",
        "✓ Файлы скачаны",
        "→ Проверяю целостность файлов (SHA-256)…",
        "✓ Целостность файлов подтверждена",
        "→ Устанавливаю файлы…",
        "✓ Файлы обновлены",
        "→ Перезапускаю сервис…",
        "✓ Сервис перезапущен",
      ],
      updateDone: (v) => `✓ Обновление до v${v} завершено! Данные сохранены.`,
      restarting: "→ Перезапускаю сервис…",
      restarted: "✓ Сервис перезапущен.",
      uninstallConfirm: "Удалить vps-net-stat? [y/N]: ",
      uninstalled: "Программа удалена.",
      uninstalledDbNote: "База данных сохранена не была (демо-режим).",
      reinstallHint: "Чтобы начать заново — введите install.sh или нажмите «↺ сброс».",
      langSwitched: "Язык переключён.",
    },
  };

  function T(){ return STRINGS[state ? state.lang : "en"]; }

  // ── Formatting helpers ──────────────────────────────────────────────────
  const UNITS = [[1024**4,"TiB"],[1024**3,"GiB"],[1024**2,"MiB"],[1024,"KiB"],[1,"B"]];
  function fmtBytes(b){
    b = b || 0;
    for (const [div, unit] of UNITS){
      if (b >= div) return (b/div).toFixed(2) + " " + unit;
    }
    return b + " B";
  }
  function pad(str, len){
    str = String(str);
    return str + " ".repeat(Math.max(0, len - str.length));
  }
  function todayISO(offsetDays = 0){
    const d = new Date();
    d.setDate(d.getDate() + offsetDays);
    return d.toISOString().slice(0,10);
  }
  function monthOf(iso){ return iso.slice(0,7); }
  function rndInt(min, max){ return Math.floor(Math.random()*(max-min+1))+min; }
  function esc(s){
    return String(s).replace(/[&<>]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;"}[c]));
  }
  function sleep(ms){ return new Promise(r => setTimeout(r, ms)); }

  // ── State ────────────────────────────────────────────────────────────────
  function genHistoryDays(nDays){
    const days = {};
    let base = rndInt(3, 9) * 1024**3;
    for (let i = nDays - 1; i >= 0; i--){
      const day = todayISO(-i);
      const variance = 0.55 + Math.random() * 0.9;
      const rx = Math.round(base * variance * (0.45 + Math.random()*0.15));
      const tx = Math.round(base * variance * (0.45 + Math.random()*0.15));
      days[day] = { rx, tx };
      base = base * (0.92 + Math.random()*0.16);
    }
    return days;
  }

  function freshState(lang){
    const traffic = genHistoryDays(10);
    return {
      installed: true,
      version: DEMO_VERSION_INSTALLED,
      lang: lang || "en",
      installedAt: todayISO(-10),
      traffic,
      watched: [],
      portTraffic: {},
      limitGiB: null,
      openPorts: [
        {proto:"tcp", port:22,  process:"sshd"},
        {proto:"tcp", port:80,  process:"nginx"},
        {proto:"tcp", port:443, process:"nginx"},
        {proto:"tcp", port:3000,process:"node"},
      ],
      shellHistory: [],   // only top-level shell commands (vns, clear, help, install.sh)
    };
  }

  function loadState(){
    try{
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return freshState("en");
      const parsed = JSON.parse(raw);
      if (!parsed || !parsed.installed) return null; // "uninstalled"
      if (!parsed.shellHistory) parsed.shellHistory = [];
      return parsed;
    }catch(e){
      return freshState("en");
    }
  }
  function saveState(){ if (state) localStorage.setItem(STORAGE_KEY, JSON.stringify(state)); }
  function wipeState(){ localStorage.removeItem(STORAGE_KEY); }

  let state = loadState();

  // ── Output helpers ──────────────────────────────────────────────────────
  function out(html, cls){
    const div = document.createElement("div");
    div.className = "line" + (cls ? " " + cls : "");
    div.innerHTML = html;
    $body.appendChild(div);
    return div;
  }
  function outRaw(text, cls){ out(esc(text), cls); }
  function blank(){ out("&nbsp;", "gap"); }
  function scrollBottom(){ $body.scrollTop = $body.scrollHeight; }

  // Clears the whole terminal viewport — mirrors a real TUI app redrawing
  // the screen (like `clear` inside vns). Used whenever we move between
  // menu screens, so the user can't scroll up and see stale state.
  function clearScreen(){ $body.innerHTML = ""; }

  function printTable(headers, rows){
    const widths = headers.map(h => h.length);
    rows.forEach(r => r.forEach((c,i) => { widths[i] = Math.max(widths[i], String(c).length); }));
    const line = (cells) => cells.map((c,i) => pad(c, widths[i])).join("  ");
    outRaw(line(headers), "dim");
    outRaw(widths.map(w => "─".repeat(w)).join("  "), "faint");
    rows.forEach(r => outRaw(line(r.map(String))));
  }

  function bar(pct, width=20){
    const filled = Math.round(Math.min(pct,1) * width);
    const cls = pct > 0.9 ? "bar-fill-r" : pct > 0.7 ? "bar-fill-y" : "bar-fill-g";
    const filledStr = "█".repeat(filled);
    const emptyStr  = "░".repeat(width - filled);
    return `<span class="${cls}">${filledStr}</span><span class="bar-track">${emptyStr}</span>`;
  }

  // ── Traffic aggregation ─────────────────────────────────────────────────
  function sumRange(pred){
    let rx=0, tx=0;
    for (const [day, v] of Object.entries(state.traffic)){
      if (pred(day)){ rx += v.rx; tx += v.tx; }
    }
    return {rx, tx};
  }
  function totalAllTime(){ return sumRange(() => true); }
  function totalToday(){ const t = todayISO(); return sumRange(d => d === t); }
  function totalMonth(){ const m = monthOf(todayISO()); return sumRange(d => monthOf(d) === m); }

  function monthlyBreakdown(){
    const map = {};
    for (const [day, v] of Object.entries(state.traffic)){
      const m = monthOf(day);
      if (!map[m]) map[m] = {rx:0, tx:0};
      map[m].rx += v.rx; map[m].tx += v.tx;
    }
    return Object.entries(map).sort((a,b)=>a[0]<b[0]?-1:1);
  }

  function lastNDays(n){
    return Object.entries(state.traffic).sort((a,b)=>a[0]<b[0]?-1:1).slice(-n);
  }

  // ── Live ticking traffic while the tab is open ─────────────────────────
  function liveTick(){
    if (!state) return;
    const today = todayISO();
    if (!state.traffic[today]) state.traffic[today] = {rx:0, tx:0};
    state.traffic[today].rx += rndInt(400_000, 4_000_000);
    state.traffic[today].tx += rndInt(300_000, 3_000_000);

    state.watched.forEach(w => {
      const key = `${w.port}/${w.proto}`;
      if (!state.portTraffic[key]) state.portTraffic[key] = {rx:0, tx:0};
      state.portTraffic[key].rx += rndInt(20_000, 250_000);
      state.portTraffic[key].tx += rndInt(15_000, 200_000);
    });
    saveState();
  }
  setInterval(liveTick, 4000);

  // ── Main menu screen ────────────────────────────────────────────────────
  function renderMainMenu(){
    const t = T();
    clearScreen();
    blank();
    out(`  <span class="menu-title-box">${esc(t.menuTitle)}</span>`);

    const verColor = state.version === DEMO_VERSION_LATEST ? "ok" : "warn";
    out(`  ${esc(t.version)} <span class="${verColor}">${state.version}</span>`);
    if (state.version !== DEMO_VERSION_LATEST){
      out(`  <span class="ok">${esc(t.newVersion)} ${DEMO_VERSION_LATEST}</span>`);
    }

    const dbSizeApprox = 2_800_000 + Object.keys(state.traffic).length * 4200 + state.watched.length * 900;
    out(`  ${esc(t.diskUsage)} ${fmtBytes(dbSizeApprox + 61_000)}  (${esc(t.diskDb)}: ${fmtBytes(dbSizeApprox)}, ${esc(t.diskApp)}: 61.00 KiB)`, "dim");

    if (state.limitGiB){
      const {rx, tx} = totalMonth();
      const usedGiB = (rx+tx) / 1024**3;
      const pct = Math.min(usedGiB / state.limitGiB, 1);
      out(`  ${esc(t.monthlyLimit)} ${bar(pct)}  ${usedGiB.toFixed(1)} / ${state.limitGiB.toFixed(0)} GiB (${Math.round(pct*100)}%)`);
    }

    blank();
    outRaw("  " + t.chooseAction, "dim");
    blank();

    t.items.forEach(([key,label]) => {
      if (key === "─"){ outRaw("  " + "─".repeat(40), "faint"); }
      else { out(`  [${key}] ${esc(label)}`); }
    });
    blank();
    outRaw("  " + t.choosePrompt, "faint");
    scrollBottom();
  }

  // ── Sub-screens (each one clears and redraws, like a real TUI) ─────────
  function screenSummary(){
    const t = T();
    clearScreen();
    const d = totalToday(), m = totalMonth(), a = totalAllTime();
    blank();
    outRaw("  " + t.summaryTitle, "dim");
    blank();
    printTable([t.period, t.incoming, t.outgoing], [
      [t.today,   fmtBytes(d.rx), fmtBytes(d.tx)],
      [t.month,   fmtBytes(m.rx), fmtBytes(m.tx)],
      [t.allTime, fmtBytes(a.rx), fmtBytes(a.tx)],
    ]);
    blank();
    out(`  ${esc(t.openPorts)} ${state.openPorts.length}`);
  }

  function screenPorts(){
    const t = T();
    clearScreen();
    blank();
    const now = new Date().toLocaleString();
    outRaw("  " + t.portsHeader(now), "dim");
    blank();
    const rows = state.openPorts.map(p => [p.proto, p.port, "LISTEN", rndInt(800,50000), p.process]);
    printTable(["Proto","Port","State","PID","Process"], rows);
    blank();
    out(`  ${esc(t.portsTotal)} ${state.openPorts.length}`);
  }

  function screenAllMonths(){
    const t = T();
    clearScreen();
    blank();
    outRaw("  " + t.allMonthsTitle, "dim");
    blank();
    const rows = monthlyBreakdown();
    if (!rows.length){ outRaw("  " + t.noData, "faint"); return; }
    let totalRx=0, totalTx=0;
    const tableRows = rows.map(([m,v]) => {
      totalRx += v.rx; totalTx += v.tx;
      return [m, fmtBytes(v.rx), fmtBytes(v.tx), fmtBytes(v.rx+v.tx)];
    });
    printTable([t.monthCol, t.incoming, t.outgoing, t.total], tableRows);
    blank();
    out(`  ${esc(t.grandTotal)}   ${fmtBytes(totalRx)}   ${fmtBytes(totalTx)}   ${fmtBytes(totalRx+totalTx)}`);
  }

  function screenDays(n){
    const t = T();
    n = n || 30;
    clearScreen();
    blank();
    outRaw("  " + t.daysTitle(n), "dim");
    blank();
    const rows = lastNDays(n);
    if (!rows.length){ outRaw("  " + t.noData, "faint"); return; }
    let totalRx=0, totalTx=0;
    const tableRows = rows.map(([day,v]) => {
      totalRx += v.rx; totalTx += v.tx;
      return [day, fmtBytes(v.rx), fmtBytes(v.tx), fmtBytes(v.rx+v.tx)];
    });
    printTable([t.dayCol, t.incoming, t.outgoing, t.total], tableRows);
    blank();
    out(`  ${esc(t.dailyTotal)}   ${fmtBytes(totalRx)}   ${fmtBytes(totalTx)}   ${fmtBytes(totalRx+totalTx)}`);
  }

  function screenPortTop(){
    const t = T();
    clearScreen();
    blank();
    outRaw("  " + t.portTopTitle, "dim");
    blank();
    const entries = Object.entries(state.portTraffic);
    if (!entries.length){
      outRaw("  " + t.portTopEmpty, "faint");
      return;
    }
    const rows = entries
      .map(([key, v]) => {
        const [port, proto] = key.split("/");
        const w = state.watched.find(w => String(w.port)===port && w.proto===proto);
        return [port, proto, (w && w.comment) || "—", fmtBytes(v.rx), fmtBytes(v.tx), fmtBytes(v.rx+v.tx), v.rx+v.tx];
      })
      .sort((a,b) => b[6]-a[6])
      .map(r => r.slice(0,6));
    printTable([t.portCol, t.protoCol, t.commentCol, t.incoming, t.outgoing, t.total], rows);
  }

  function screenCharts(n){
    const t = T();
    n = n || 7;
    clearScreen();
    blank();
    outRaw("  " + t.chartsTitle(n), "dim");
    blank();
    const rows = lastNDays(n);
    if (!rows.length){ outRaw("  " + t.chartsEmpty, "faint"); return; }
    const maxVal = Math.max(...rows.map(([,v]) => v.rx+v.tx), 1);
    const width = 30;
    rows.forEach(([day, v]) => {
      const label = day.slice(5);
      const rxLen = Math.round(v.rx / maxVal * width);
      const txLen = Math.round(v.tx / maxVal * width);
      const rxBar = `<span class="ok">${"█".repeat(rxLen)}</span>`;
      const txBar = `<span class="accent">${"█".repeat(txLen)}</span>`;
      out(`  ${label}  ${rxBar}${txBar}  ${fmtBytes(v.rx+v.tx)}`);
    });
    blank();
    out(`  <span class="ok">█</span> ${esc(t.chartsIncoming)}   <span class="accent">█</span> ${esc(t.chartsOutgoing)}`);
    const totalRx = rows.reduce((s,[,v])=>s+v.rx,0);
    const totalTx = rows.reduce((s,[,v])=>s+v.tx,0);
    blank();
    out(`  ${esc(t.chartsTotal)} ${fmtBytes(totalRx+totalTx)}  (${esc(t.chartsIncoming)}: ${fmtBytes(totalRx)}, ${esc(t.chartsOutgoing)}: ${fmtBytes(totalTx)})`);
  }

  function screenWatchedList(){
    const t = T();
    clearScreen();
    blank();
    outRaw("  " + t.watchedTitle, "dim");
    blank();
    if (!state.watched.length){
      outRaw("  " + t.watchedEmpty, "faint");
      return;
    }
    const rows = state.watched.map(w => {
      const key = `${w.port}/${w.proto}`;
      const v = state.portTraffic[key] || {rx:0,tx:0};
      return [w.port, w.proto, w.comment || "—", w.added, fmtBytes(v.rx), fmtBytes(v.tx), fmtBytes(v.rx+v.tx)];
    });
    printTable([t.portCol, t.protoCol, t.commentCol, t.addedCol, t.incoming, t.outgoing, t.total], rows);
  }

  function screenInfo(){
    const t = T();
    clearScreen();
    blank();
    outRaw("  " + t.infoTitle, "dim");
    blank();
    out(`  <span class="ok">${esc(t.svcRunning)}</span>`);
    out(`  ${esc(t.uptime)}      ${rndInt(1,9)}d ${rndInt(0,23)}h ${rndInt(0,59)}m`, "dim");
    out(`  ${esc(t.lastScan)}    ${rndInt(2,58)} ${esc(t.secAgo)}`, "dim");
    out(`  ${esc(t.tracked)}     ${state.watched.length}`, "dim");
    out(`  ${esc(t.backend)}     ${esc(t.backendVal)}`, "dim");
  }

  function screenDoctor(){
    const t = T();
    clearScreen();
    blank();
    outRaw("  " + t.doctorTitle, "dim");
    blank();
    t.doctorChecks.forEach(c => out(`  <span class="ok">✓</span> ${esc(c)}`));
    out(`  <span class="ok">✓</span> ${esc(t.doctorDisk(fmtBytes(rndInt(8,40) * 1024**3)))}`);
    out(`  <span class="ok">✓</span> ${esc(t.doctorFresh)}`);
    blank();
    outRaw("  " + t.doctorAllOk, "ok");
  }

  // ── Actions on state ────────────────────────────────────────────────────
  function actionResetServer(){
    state.traffic = {};
    saveState();
    blank();
    outRaw("  " + T().resetServerDone, "ok");
  }
  function actionResetPort(portStr){
    const t = T();
    const port = parseInt(portStr, 10);
    if (!port){ outRaw("  " + t.invalidPort, "err"); return; }
    Object.keys(state.portTraffic).forEach(key => {
      if (key.startsWith(port + "/")) delete state.portTraffic[key];
    });
    saveState();
    out("  " + esc(t.resetPortDone(port)), "ok");
  }

  function actionWatchAdd(args){
    const t = T();
    const port = parseInt(args[0], 10);
    if (!port || port < 1 || port > 65535){
      outRaw("  " + t.invalidPort, "err");
      return;
    }
    let protos = ["tcp"];
    let commentStart = 1;
    if (args[1] === "udp"){ protos = ["udp"]; commentStart = 2; }
    else if (args[1] === "both"){ protos = ["tcp","udp"]; commentStart = 2; }
    else if (args[1] === "tcp"){ protos = ["tcp"]; commentStart = 2; }
    const comment = args.slice(commentStart).join(" ") || null;

    let added = 0;
    protos.forEach(proto => {
      const exists = state.watched.find(w => w.port === port && w.proto === proto);
      if (!exists){
        state.watched.push({port, proto, comment, added: todayISO()});
        state.portTraffic[`${port}/${proto}`] = {rx:0, tx:0};
        added++;
      }
    });
    saveState();
    blank();
    if (added) outRaw("  " + t.portAdded, "ok");
    else outRaw("  " + t.portAlready, "warn");
  }

  function actionWatchDel(args){
    const t = T();
    const port = parseInt(args[0], 10);
    if (!port){ outRaw("  " + t.invalidPort, "err"); return; }
    const before = state.watched.length;
    state.watched = state.watched.filter(w => w.port !== port);
    Object.keys(state.portTraffic).forEach(key => {
      if (key.startsWith(port + "/")) delete state.portTraffic[key];
    });
    saveState();
    blank();
    if (state.watched.length < before) outRaw("  " + t.portRemoved, "ok");
    else outRaw("  " + t.portNotFound, "warn");
  }

  function actionSetLimit(args){
    const t = T();
    const val = parseFloat(args[0]);
    blank();
    if (Number.isNaN(val)){
      outRaw("  " + t.limitInvalid, "err");
      return;
    }
    state.limitGiB = val > 0 ? val : null;
    saveState();
    if (state.limitGiB) out("  " + esc(t.limitSet(state.limitGiB)), "ok");
    else outRaw("  " + t.limitDisabled, "ok");
  }

  // Realistic, multi-step "update" with delays — takes ~10-15s total,
  // like the real update.sh does over the network.
  async function actionUpdate(){
    const t = T();
    blank();
    if (state.version === DEMO_VERSION_LATEST){
      out("  " + esc(t.alreadyLatest(state.version)), "ok");
      return;
    }
    outRaw("  " + t.updating(state.version, DEMO_VERSION_LATEST), "warn");
    setInputEnabled(false);
    for (const step of t.updateSteps){
      const isOk = step.startsWith("✓");
      await sleep(rndInt(900, 1700));
      outRaw("  " + step, isOk ? "ok" : "dim");
      scrollBottom();
    }
    await sleep(600);
    state.version = DEMO_VERSION_LATEST;
    saveState();
    out("  " + esc(t.updateDone(DEMO_VERSION_LATEST)), "ok");
    setInputEnabled(true);
  }

  async function actionRestart(){
    const t = T();
    blank();
    outRaw("  " + t.restarting, "dim");
    setInputEnabled(false);
    await sleep(rndInt(1200, 2000));
    outRaw("  " + t.restarted, "ok");
    setInputEnabled(true);
  }

  function actionUninstall(){
    const t = T();
    blank();
    outRaw("  " + t.uninstalled, "err");
    outRaw("  " + t.uninstalledDbNote, "faint");
    wipeState();
    state = null;
    blank();
    outRaw("  " + t.reinstallHint, "faint");
  }

  // ── Install flow (state === null) ───────────────────────────────────────
  async function runInstall(){
    const langForInstall = currentUiLang();
    state = freshState(langForInstall);
    saveState();
    const t = T();
    blank();
    setInputEnabled(false);
    for (const step of t.installing){
      const isOk = step.startsWith("✓");
      await sleep(rndInt(350, 650));
      outRaw("  " + step, isOk ? "ok" : "dim");
      scrollBottom();
    }
    blank();
    out(`  <span class="ok">${esc(t.installDone(state.version))}</span>`);
    blank();
    outRaw("  " + t.installHint, "faint");
    setInputEnabled(true);
  }

  // Remembers last chosen UI language even across an uninstall, so a
  // fresh install keeps speaking the language the visitor picked.
  function currentUiLang(){
    try {
      return localStorage.getItem("vns_demo_lang_pref") || "en";
    } catch(e){ return "en"; }
  }
  function rememberUiLang(lang){
    try { localStorage.setItem("vns_demo_lang_pref", lang); } catch(e){}
  }

  // ── Command processor ───────────────────────────────────────────────────
  let mode = "shell";        // "shell" | "menu" | "await:*"
  let pendingAction = null;
  let inputEnabled = true;

  let activeInput = null; // direct reference to the live <input>, kept in
                           // sync by buildInputRow() — safer than querying
                           // the DOM, since output lines get appended after
                           // the prompt row while an action is running.

  function setInputEnabled(v){
    inputEnabled = v;
    if (activeInput){
      activeInput.disabled = !v;
      // Browsers drop focus automatically when an input becomes disabled
      // and don't restore it when re-enabled — so we do it ourselves,
      // otherwise Enter silently stops working until the user clicks back in.
      if (v) activeInput.focus();
    }
  }
  function currentInput(){ return activeInput; }

  function enterMenu(){
    mode = "menu";
    renderMainMenu();
  }

  function handleMenuChoice(raw){
    const t = T();
    const choice = raw.trim();
    if (choice === "0"){
      mode = "shell";
      clearScreen();
      outRaw("  " + t.menuClosed, "dim");
      return;
    }
    if (["1","2","3","4","5","6","7","8","9","10","11","12","13","14","15","16","17","18","19"].includes(choice)){
      switch(choice){
        case "1": screenSummary(); break;
        case "2": screenPorts(); break;
        case "3": screenAllMonths(); break;
        case "4": screenDays(30); break;
        case "5": screenPortTop(); break;
        case "6": screenCharts(7); break;
        case "7":
          clearScreen(); blank();
          outRaw("  " + t.portPrompt, "dim");
          mode = "await:addport";
          return;
        case "8":
          screenWatchedList();
          blank();
          outRaw("  " + t.portDelPrompt, "dim");
          mode = "await:delport";
          return;
        case "9": screenWatchedList(); break;
        case "10":
          clearScreen(); blank();
          outRaw("  " + t.resetServerConfirm, "warn");
          mode = "await:resetserver";
          return;
        case "11":
          screenWatchedList();
          blank();
          outRaw("  " + t.resetPortNumberPrompt, "dim");
          mode = "await:resetport";
          return;
        case "12":
          clearScreen(); blank();
          outRaw("  " + t.exportImportUnavailable, "faint");
          break;
        case "13": {
          const cur = state.limitGiB ? state.limitGiB + " GiB" : t.limitNone;
          clearScreen(); blank();
          out("  " + esc(t.limitCurrent(cur)));
          outRaw("  " + t.limitPrompt, "dim");
          mode = "await:setlimit";
          return;
        }
        case "14": screenInfo(); break;
        case "15": screenDoctor(); break;
        case "16":
          clearScreen(); blank();
          outRaw("  " + t.uninstallConfirm, "err");
          mode = "await:uninstall";
          return;
        case "17":
          clearScreen();
          mode = "await:updating";
          actionUpdate().then(() => {
            blank();
            outRaw("  " + t.pressEnter, "faint");
            mode = "await:pause";
          });
          return;
        case "18":
          clearScreen();
          mode = "await:restarting";
          actionRestart().then(() => {
            blank();
            outRaw("  " + t.pressEnter, "faint");
            mode = "await:pause";
          });
          return;
        case "19": {
          const newLang = state.lang === "ru" ? "en" : "ru";
          state.lang = newLang;
          rememberUiLang(newLang);
          saveState();
          applyStaticI18n();
          clearScreen();
          blank();
          outRaw("  " + STRINGS[newLang].langSwitched, "ok");
          break;
        }
      }
      blank();
      outRaw("  " + t.pressEnter, "faint");
      mode = "await:pause";
      return;
    }
    blank();
    outRaw("  " + t.unknownMenuItem, "err");
  }

  function handleAwait(raw){
    const t = T();
    const val = raw.trim();

    if (mode === "await:pause"){
      renderMainMenu();
      mode = "menu";
      return;
    }
    if (mode === "await:addport"){
      pendingAction = { port: val };
      mode = "await:addport:proto";
      blank();
      outRaw("  " + t.protoPrompt, "dim");
      outRaw("  " + t.protoArrow, "dim");
      return;
    }
    if (mode === "await:addport:proto"){
      const protoMap = {"1":"tcp","2":"udp","3":"both","":"tcp"};
      pendingAction.proto = protoMap[val] ?? "tcp";
      mode = "await:addport:comment";
      blank();
      outRaw("  " + t.commentPrompt, "dim");
      return;
    }
    if (mode === "await:addport:comment"){
      actionWatchAdd([pendingAction.port, pendingAction.proto, val]);
      pendingAction = null;
      blank();
      outRaw("  " + t.pressEnter, "faint");
      mode = "await:pause";
      return;
    }
    if (mode === "await:delport"){
      actionWatchDel([val]);
      blank();
      outRaw("  " + t.pressEnter, "faint");
      mode = "await:pause";
      return;
    }
    if (mode === "await:resetserver"){
      if (val.toLowerCase() === "y") actionResetServer();
      else { blank(); outRaw("  " + t.cancelled, "dim"); }
      blank();
      outRaw("  " + t.pressEnter, "faint");
      mode = "await:pause";
      return;
    }
    if (mode === "await:resetport"){
      pendingAction = { port: val };
      mode = "await:resetport:confirm";
      blank();
      out("  " + esc(t.resetPortConfirm(val)), "warn");
      return;
    }
    if (mode === "await:resetport:confirm"){
      if (val.toLowerCase() === "y") actionResetPort(pendingAction.port);
      else { blank(); outRaw("  " + t.cancelled, "dim"); }
      pendingAction = null;
      blank();
      outRaw("  " + t.pressEnter, "faint");
      mode = "await:pause";
      return;
    }
    if (mode === "await:setlimit"){
      actionSetLimit([val]);
      blank();
      outRaw("  " + t.pressEnter, "faint");
      mode = "await:pause";
      return;
    }
    if (mode === "await:uninstall"){
      if (val.toLowerCase() === "y"){
        actionUninstall();
        mode = "shell";
      } else {
        blank();
        outRaw("  " + t.cancelled, "dim");
        blank();
        outRaw("  " + t.pressEnter, "faint");
        mode = "await:pause";
      }
      return;
    }
    // await:updating / await:restarting — input is disabled during these,
    // so no line should reach here, but guard just in case.
  }

  function handleShellCommand(raw){
    const t = T();
    const trimmed = raw.trim();
    if (!trimmed) return;
    const parts = trimmed.split(/\s+/);
    const cmd = parts[0];

    if (state === null){
      if (/install\.sh/.test(trimmed) || trimmed === "install"){
        mode = "await:installing";
        runInstall().then(() => { mode = "shell"; });
        return;
      }
      if (cmd === "vns"){
        blank();
        T_noState().vnsNotFound.forEach(l => outRaw("  " + l, "err"));
        outRaw("  " + T_noState().installCmdHint, "accent");
        return;
      }
      if (cmd === "help" || cmd === "clear"){
        // fall through
      } else {
        blank();
        out("  " + esc(T_noState().bashNotFound(cmd)), "err");
        return;
      }
    }

    switch(cmd){
      case "vns":
        if (state) enterMenu();
        return;
      case "clear":
        clearScreen();
        return;
      case "help": {
        const tt = state ? t : T_noState();
        blank();
        outRaw("  " + tt.helpTitle, "dim");
        out(`  <b>vns</b>            — ${esc(tt.helpVns)}`);
        out(`  <b>clear</b>          — ${esc(tt.helpClear)}`);
        out(`  <b>help</b>           — ${esc(tt.helpHelp)}`);
        if (state === null){
          out(`  <b>install.sh</b>     — ${esc(tt.helpInstall)}`);
        }
        return;
      }
      default:
        blank();
        out("  " + esc((state ? t : T_noState()).unknownCmd(cmd)), "err");
        return;
    }
  }

  // English fallback strings used when state is null (not installed yet) —
  // we still respect the visitor's last chosen UI language if we have one.
  function T_noState(){ return STRINGS[currentUiLang()]; }

  // ── Input routing ────────────────────────────────────────────────────────
  function handleLine(raw){
    const sigil = state === null ? "$" : "root@demo-vps:~#";
    out(`<span class="accent">${sigil}</span> ${esc(raw)}`, null);
    if (mode === "shell") handleShellCommand(raw);
    else if (mode === "menu") handleMenuChoice(raw);
    else handleAwait(raw);
    scrollBottom();
  }

  // ── Static (non-terminal) i18n: header, hint bar, buttons ──────────────
  function applyStaticI18n(){
    const t = state ? T() : T_noState();
    document.documentElement.lang = (state ? state.lang : currentUiLang());
    $brandTag.textContent = t.brandTag;
    $langBtn.textContent = (state ? state.lang : currentUiLang()) === "ru" ? "EN" : "RU";
    $langBtn.title = "Switch language";
    $resetBtn.textContent = t.resetBtn;
    $hint.innerHTML =
      `<span>${t.hintOpen.replace("{vns}","<kbd>vns</kbd>").replace("{Enter}","<kbd>Enter</kbd>")}</span>` +
      `<span>${t.hintHistory.replace("{↑}","<kbd>↑</kbd>").replace("{↓}","<kbd>↓</kbd>")}</span>`;
  }

  // ── Boot / welcome ──────────────────────────────────────────────────────
  function boot(){
    applyStaticI18n();
    const t = state ? T() : T_noState();
    outRaw("  " + t.welcome, "dim");
    blank();
    if (state === null){
      outRaw("  " + t.notInstalled, "warn");
      outRaw("  " + t.typeInstall, "accent");
    } else {
      outRaw("  " + t.alreadyInstalled, "dim");
      outRaw("  " + t.typeVns, "accent");
    }
    blank();
    outRaw("  " + t.helpHint, "faint");
    scrollBottom();
  }

  // ── Input row (manually drawn on top of the output stream) ─────────────
  function buildInputRow(){
    const row = document.createElement("div");
    row.className = "prompt-row";
    const sigil = document.createElement("span");
    sigil.className = "prompt-sigil";
    sigil.textContent = state === null ? "$" : "root@demo-vps:~#";
    const input = document.createElement("input");
    input.className = "prompt-input";
    input.type = "text";
    input.autocomplete = "off";
    input.autocapitalize = "off";
    input.spellcheck = false;
    input.disabled = !inputEnabled;
    input.placeholder = mode === "shell" ? "vns" : "";
    row.appendChild(sigil);
    row.appendChild(input);
    $body.appendChild(row);
    activeInput = input;
    input.focus();

    // Command history only tracks top-level shell commands — never menu
    // digits or prompt answers, exactly like a real shell would.
    let cmdHistory = state ? (state.shellHistory || []) : [];
    let histIdx = cmdHistory.length;

    input.addEventListener("keydown", (e) => {
      if (input.disabled) { e.preventDefault(); return; }
      if (e.key === "Enter"){
        const val = input.value;
        const wasShellMode = mode === "shell";
        row.remove();
        activeInput = null;
        if (wasShellMode && state && val.trim()){
          state.shellHistory = state.shellHistory || [];
          state.shellHistory.push(val);
          if (state.shellHistory.length > 200) state.shellHistory.shift();
          saveState();
        }
        handleLine(val);
        buildInputRow();
      } else if (e.key === "ArrowUp"){
        e.preventDefault();
        if (mode !== "shell") return;
        if (histIdx > 0){ histIdx--; input.value = cmdHistory[histIdx] || ""; }
      } else if (e.key === "ArrowDown"){
        e.preventDefault();
        if (mode !== "shell") return;
        if (histIdx < cmdHistory.length){ histIdx++; input.value = cmdHistory[histIdx] || ""; }
      } else if (e.key === "Tab"){
        e.preventDefault();
        if (mode === "shell" && "vns".startsWith(input.value)) input.value = "vns";
      }
    });
  }

  $body.addEventListener("click", () => {
    const input = currentInput();
    if (input && !input.disabled) input.focus();
  }, {passive:true});

  // ── Language button ──────────────────────────────────────────────────────
  $langBtn.addEventListener("click", () => {
    if (!inputEnabled) return;
    const newLang = (state ? state.lang : currentUiLang()) === "ru" ? "en" : "ru";
    rememberUiLang(newLang);
    if (state){ state.lang = newLang; saveState(); }
    applyStaticI18n();
    clearScreen();
    mode = "shell";
    boot();
    buildInputRow();
  });

  // ── Reset button ──────────────────────────────────────────────────────────
  $resetBtn.addEventListener("click", () => {
    const t = state ? T() : T_noState();
    if (!confirm(t.resetConfirm)) return;
    const lang = state ? state.lang : currentUiLang();
    wipeState();
    state = freshState(lang);
    saveState();
    clearScreen();
    mode = "shell";
    boot();
    buildInputRow();
  });

  // ── Start ────────────────────────────────────────────────────────────────
  boot();
  buildInputRow();

})();
