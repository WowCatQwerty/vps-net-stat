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
  const $heroInner = document.getElementById("heroInner");
  const $scrollCueText = document.getElementById("scrollCueText");
  const $heroLangBtn = document.getElementById("heroLangBtn");

  // ── i18n ────────────────────────────────────────────────────────────────
  const STRINGS = {
    en: {
      brandTag: "— interactive demo menu",
      heroTagline: "Simple <b>network traffic and port monitor</b> for Linux servers. Tracks traffic by day and month, watches open ports with process names, and counts <b>exact per-port traffic</b> via iptables/nftables. Data lives in SQLite and survives reboots.",
      heroBadges: ["GPLv3 · Open Source", "Python 3", "systemd", "SQLite", "iptables / nftables", "IPv6"],
      heroFeature1Title: "Exact per-port traffic",
      heroFeature1Desc: "Real byte counters via firewall rules — not estimates, not sampling.",
      heroFeature2Title: "Survives reboots",
      heroFeature2Desc: "History stored in SQLite, accumulates indefinitely by default.",
      heroFeature3Title: "Interactive TUI menu",
      heroFeature3Desc: "No config files to edit — everything through a friendly terminal menu.",
      heroBtnDemo: "Try the live demo ↓",
      heroBtnGithub: "View on GitHub",
      scrollCue: "Scroll for demo",
      hintOpen: "Type {vns} and press {Enter} to open the menu",
      hintHistory: "{↑}/{↓} command history",
      resetBtn: "↺ reset",
      resetConfirm: "Reset the demo? All fake traffic, watched ports, and settings will be cleared, and it'll return to the default state (v4.4.3).",
      welcome: "Welcome to the vps-net-stat demo.",
      alreadyInstalled: "vps-net-stat is already \"installed\" — as if you came back to your own server.",
      typeVns: "Type:  vns",
      helpHint: "Hint: help — list of available demo commands.",
      helpTitle: "Available demo commands:",
      helpVns: "open the interactive menu",
      helpClear: "clear the screen",
      helpHelp: "this help text",
      unknownCmd: (c) => `bash: ${c}: command not found. Type help.`,
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
      uninstallResetNote: "Session reset to a fresh install (v4.4.3) — type vns to open the menu again.",
      langSwitched: "Language switched.",
    },
    ru: {
      brandTag: "— интерактивное демо меню",
      heroTagline: "Простой <b>монитор трафика и портов</b> для Linux-серверов. Считает трафик по дням и месяцам, отслеживает открытые порты с именами процессов и точно считает <b>трафик по каждому порту</b> через iptables/nftables. Данные хранятся в SQLite и переживают перезагрузки.",
      heroBadges: ["GPLv3 · Открытый код", "Python 3", "systemd", "SQLite", "iptables / nftables", "IPv6"],
      heroFeature1Title: "Точный трафик по портам",
      heroFeature1Desc: "Настоящие байтовые счётчики через правила файрвола — не оценка, не выборка.",
      heroFeature2Title: "Переживает перезагрузки",
      heroFeature2Desc: "История хранится в SQLite и копится бесконечно по умолчанию.",
      heroFeature3Title: "Интерактивное TUI-меню",
      heroFeature3Desc: "Не нужно редактировать конфиги — всё через удобное меню в терминале.",
      heroBtnDemo: "Попробовать демо ↓",
      heroBtnGithub: "Открыть на GitHub",
      scrollCue: "Прокрутите к демо",
      hintOpen: "Введите {vns} и нажмите {Enter}, чтобы открыть меню",
      hintHistory: "{↑}/{↓} история команд",
      resetBtn: "↺ сброс",
      resetConfirm: "Сбросить демо? Весь фейковый трафик, отслеживаемые порты и настройки будут очищены, демо вернётся к состоянию по умолчанию (v4.4.3).",
      welcome: "Добро пожаловать в демо vps-net-stat.",
      alreadyInstalled: "vps-net-stat уже «установлен» — как будто вы вернулись на свой сервер.",
      typeVns: "Наберите:  vns",
      helpHint: "Подсказка: help — список доступных демо-команд.",
      helpTitle: "Доступные команды демо:",
      helpVns: "открыть интерактивное меню",
      helpClear: "очистить экран",
      helpHelp: "эта справка",
      unknownCmd: (c) => `bash: ${c}: команда не найдена. Наберите help.`,
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
      uninstallResetNote: "Сессия сброшена к свежей установке (v4.4.3) — наберите vns, чтобы снова открыть меню.",
      langSwitched: "Язык переключён.",
    },
  };

  function T(){ return STRINGS[state.lang]; }

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
      shellHistory: [],   // only top-level shell commands (vns, clear, help)
    };
  }

  function loadState(){
    try{
      const raw = sessionStorage.getItem(STORAGE_KEY);
      if (!raw) return freshState(currentUiLang()); // fresh visit — program is "pre-installed"
      const parsed = JSON.parse(raw);
      if (!parsed || !parsed.installed) return freshState(currentUiLang());
      if (!parsed.shellHistory) parsed.shellHistory = [];
      return parsed;
    }catch(e){
      return freshState(currentUiLang());
    }
  }
  function saveState(){ sessionStorage.setItem(STORAGE_KEY, JSON.stringify(state)); }

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
    const lang = state.lang;
    blank();
    outRaw("  " + t.uninstalled, "err");
    state = freshState(lang);
    saveState();
    blank();
    outRaw("  " + t.uninstallResetNote, "faint");
  }

  // Remembers last chosen UI language even across a reset, so a fresh
  // session keeps speaking the language the visitor picked before.
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
      if (v) activeInput.focus({ preventScroll: true });
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
    const cmd = trimmed.split(/\s+/)[0];

    switch(cmd){
      case "vns":
        enterMenu();
        return;
      case "clear":
        clearScreen();
        return;
      case "help":
        blank();
        outRaw("  " + t.helpTitle, "dim");
        out(`  <b>vns</b>            — ${esc(t.helpVns)}`);
        out(`  <b>clear</b>          — ${esc(t.helpClear)}`);
        out(`  <b>help</b>           — ${esc(t.helpHelp)}`);
        return;
      default:
        blank();
        out("  " + esc(t.unknownCmd(cmd)), "err");
        return;
    }
  }

  // ── Input routing ────────────────────────────────────────────────────────
  function handleLine(raw){
    out(`<span class="accent">root@demo-vps:~#</span> ${esc(raw)}`, null);
    if (mode === "shell") handleShellCommand(raw);
    else if (mode === "menu") handleMenuChoice(raw);
    else handleAwait(raw);
    scrollBottom();
  }

  // ── Static (non-terminal) i18n: header, hint bar, buttons ──────────────
  function renderHero(){
    const t = T();
    const badgesHtml = t.heroBadges.map((b, i) =>
      `<span class="hero-badge${i === 0 ? ' accent-badge' : ''}">${esc(b)}</span>`
    ).join("");

    $heroInner.innerHTML = `
      <div class="hero-mark">
        <svg viewBox="0 0 100 100" fill="none"><path d="M20 65 L38 35 L52 55 L65 30 L80 60" stroke="#4a9eff" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"/></svg>
      </div>
      <h1 class="hero-title">vps-net-stat</h1>
      <p class="hero-tagline">${t.heroTagline}</p>
      <div class="hero-badges">${badgesHtml}</div>
      <div class="hero-features">
        <div class="feature-card">
          <div class="feature-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"/><path d="M18 17V9M13 17V5M8 17v-3"/></svg>
          </div>
          <div class="feature-title">${esc(t.heroFeature1Title)}</div>
          <div class="feature-desc">${esc(t.heroFeature1Desc)}</div>
        </div>
        <div class="feature-card">
          <div class="feature-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>
          </div>
          <div class="feature-title">${esc(t.heroFeature2Title)}</div>
          <div class="feature-desc">${esc(t.heroFeature2Desc)}</div>
        </div>
        <div class="feature-card">
          <div class="feature-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="16" rx="2"/><path d="M3 9h18M8 4v5"/></svg>
          </div>
          <div class="feature-title">${esc(t.heroFeature3Title)}</div>
          <div class="feature-desc">${esc(t.heroFeature3Desc)}</div>
        </div>
      </div>
      <div class="hero-links">
        <button class="hero-btn primary" id="scrollToDemoBtn" type="button">${esc(t.heroBtnDemo)}</button>
        <a class="hero-btn secondary" href="https://github.com/WowCatQwerty/vps-net-stat" target="_blank" rel="noopener">${esc(t.heroBtnGithub)}</a>
      </div>
    `;
    $scrollCueText.textContent = t.scrollCue;
  }

  function applyStaticI18n(){
    const t = T();
    document.documentElement.lang = state.lang;
    $brandTag.textContent = t.brandTag;
    $langBtn.textContent = state.lang === "ru" ? "EN" : "RU";
    $langBtn.title = "Switch language";
    $heroLangBtn.textContent = state.lang === "ru" ? "EN" : "RU";
    $heroLangBtn.title = "Switch language";
    $resetBtn.textContent = t.resetBtn;
    $hint.innerHTML =
      `<span>${t.hintOpen.replace("{vns}","<kbd>vns</kbd>").replace("{Enter}","<kbd>Enter</kbd>")}</span>` +
      `<span>${t.hintHistory.replace("{↑}","<kbd>↑</kbd>").replace("{↓}","<kbd>↓</kbd>")}</span>`;
    renderHero();
  }

  // ── Boot / welcome ──────────────────────────────────────────────────────
  function boot(){
    applyStaticI18n();
    const t = T();
    outRaw("  " + t.welcome, "dim");
    blank();
    outRaw("  " + t.alreadyInstalled, "dim");
    outRaw("  " + t.typeVns, "accent");
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
    sigil.textContent = "root@demo-vps:~#";
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
    // preventScroll is essential here: this input lives inside the second
    // full-screen slide (the terminal). Without it, focusing an off-screen
    // element makes the browser auto-scroll the whole page to reveal it —
    // which is exactly what was causing the page to load already jumped
    // to the terminal instead of the hero on first paint.
    input.focus({ preventScroll: true });

    // Command history only tracks top-level shell commands — never menu
    // digits or prompt answers, exactly like a real shell would.
    let cmdHistory = state.shellHistory || [];
    let histIdx = cmdHistory.length;

    input.addEventListener("keydown", (e) => {
      if (input.disabled) { e.preventDefault(); return; }
      if (e.key === "Enter"){
        const val = input.value;
        const wasShellMode = mode === "shell";
        row.remove();
        activeInput = null;
        if (wasShellMode && val.trim()){
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
    if (input && !input.disabled) input.focus({ preventScroll: true });
  }, {passive:true});

  // ── Language button ──────────────────────────────────────────────────────
  function switchLanguage(){
    if (!inputEnabled) return;
    const newLang = state.lang === "ru" ? "en" : "ru";
    state.lang = newLang;
    rememberUiLang(newLang);
    saveState();
    applyStaticI18n();
    clearScreen();
    mode = "shell";
    boot();
    buildInputRow();
  }
  $langBtn.addEventListener("click", switchLanguage);
  $heroLangBtn.addEventListener("click", switchLanguage);

  // ── Reset button ──────────────────────────────────────────────────────────
  // Always returns to the same fresh v4.4.3 baseline — same outcome as
  // closing the tab (sessionStorage clears) or using menu item [16]
  // Uninstall. There is no "not installed" limbo state in this demo.
  $resetBtn.addEventListener("click", () => {
    if (!inputEnabled) return; // don't allow resetting mid-update/restart
    const t = T();
    if (!confirm(t.resetConfirm)) return;
    const lang = state.lang;
    state = freshState(lang);
    saveState();
    clearScreen();
    mode = "shell";
    boot();
    buildInputRow();
  });

  // ── Fullscreen slide (hero ⇄ demo terminal) ─────────────────────────────
  // A deliberate, JS-driven multi-second glide — the browser's own smooth
  // scroll / scroll-snap correction is too short and not tunable to last
  // "a couple of seconds", so we drive #slideTrack's transform ourselves
  // with an explicit CSS transition. Wheel (desktop) and touch swipe
  // (mobile) both call the same goToSlide() so the experience is
  // consistent everywhere — importantly, `wheel` events never fire for
  // touch scrolling at all, so touch needs its own gesture handling.
  // While the cursor/finger is over the terminal output and there's still
  // unread content to scroll through, that inner scroll takes priority —
  // the slide only reacts once it's at the edge.
  const $slideTrack = document.getElementById("slideTrack");
  let currentSlide = 0; // 0 = hero, 1 = demo
  let slideAnimating = false;
  const SLIDE_COUNT = 2;
  const SLIDE_ANIM_MS = 1700; // keep in sync with the CSS transition duration on #slideTrack
  // Trackpads and "free-spin" mice keep sending momentum/inertia wheel
  // events for a few hundred ms after the physical gesture actually ends.
  // If that tail arrives after slideAnimating has already reset, a stray
  // late event (sometimes with a flipped sign as the momentum settles)
  // can yank the page to the next/previous slide well after it has
  // already glided into place — this extra buffer swallows that tail.
  const WHEEL_COOLDOWN_MS = SLIDE_ANIM_MS + 700;

  // Explicit starting value before any interaction — some browsers won't
  // smoothly interpolate the very first change to a property that never
  // had an inline value, treating it as part of initial layout rather
  // than a transition.
  $slideTrack.style.transform = "translateY(0px)";

  function goToSlide(index){
    index = Math.max(0, Math.min(SLIDE_COUNT - 1, index));
    if (index === currentSlide) return;
    currentSlide = index;
    slideAnimating = true;
    // Defensive: explicitly guarantee the CSS transition is active before
    // every single slide change, regardless of what else might have
    // touched this element's inline style. Cheap and removes an entire
    // category of "transition silently got disabled somewhere" bugs.
    $slideTrack.style.transition = "";
    $slideTrack.style.transform = `translateY(-${currentSlide * 100}vh)`;
    setTimeout(() => { slideAnimating = false; }, WHEEL_COOLDOWN_MS);
  }

  function isScrollableAtEdge(el, deltaY){
    // True if el has no more room to scroll in the given direction —
    // meaning the page-level slide should take over instead of the element.
    if (!el) return true;
    const atTop = el.scrollTop <= 0;
    const atBottom = Math.ceil(el.scrollTop + el.clientHeight) >= el.scrollHeight;
    if (deltaY < 0) return atTop;
    if (deltaY > 0) return atBottom;
    return true;
  }

  function findScrollableAncestor(target){
    if (!target || !target.closest) return null;
    return target.closest(".term-body") || target.closest(".hero") || null;
  }

  window.addEventListener("wheel", (e) => {
    if (slideAnimating){ e.preventDefault(); return; }
    const scrollable = findScrollableAncestor(e.target);
    if (scrollable && !isScrollableAtEdge(scrollable, e.deltaY)) return; // let it scroll natively
    e.preventDefault();
    if (e.deltaY > 10) goToSlide(currentSlide + 1);
    else if (e.deltaY < -10) goToSlide(currentSlide - 1);
  }, { passive: false });

  // Touch swipe — kept passive throughout (native scroll inside the
  // terminal is never blocked mid-gesture); we only decide whether to
  // ALSO trigger a slide change once the gesture ends, based on the net
  // direction and whether the touch started at a scrollable edge.
  let touchStartY = null;
  let touchStartScrollable = null;

  window.addEventListener("touchstart", (e) => {
    if (slideAnimating || !e.touches.length) return;
    touchStartY = e.touches[0].clientY;
    touchStartScrollable = findScrollableAncestor(e.target);
  }, { passive: true });

  window.addEventListener("touchend", (e) => {
    if (slideAnimating || touchStartY === null || !e.changedTouches.length) return;
    const deltaY = touchStartY - e.changedTouches[0].clientY; // >0 = swiped up
    touchStartY = null;
    if (Math.abs(deltaY) < 50) return; // too small to count as a deliberate swipe
    if (touchStartScrollable && !isScrollableAtEdge(touchStartScrollable, deltaY)) return;
    if (deltaY > 0) goToSlide(currentSlide + 1);
    else goToSlide(currentSlide - 1);
  }, { passive: true });

  function scrollToDemoSlide(){ goToSlide(1); }
  document.getElementById("scrollCue").addEventListener("click", scrollToDemoSlide);
  // The "Try the live demo" button lives inside #heroInner, which is fully
  // re-rendered on every renderHero() call (boot + language switch), so a
  // direct listener on the button would be lost on re-render. Delegating
  // from the stable #heroInner parent survives that.
  $heroInner.addEventListener("click", (e) => {
    if (e.target.closest("#scrollToDemoBtn")) scrollToDemoSlide();
  });

  // ── Start ────────────────────────────────────────────────────────────────
  boot();
  buildInputRow();

})();
