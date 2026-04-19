"use client";

import { useMemo, useState } from "react";
import {
  ParsedEvent,
  ParsedTranscript,
  TranscriptTurn,
  UsageSummary,
  formatCost,
  formatDuration,
  formatNumber,
  parseTranscriptSource
} from "../lib/transcript";

type Filter = "all" | "messages" | "tools" | "results" | "errors";

const exampleName = "/data/shared/geophysics_agent_data/cc_convo_ex.jsonl";

export default function Home() {
  const [transcript, setTranscript] = useState<ParsedTranscript | null>(null);
  const [fileName, setFileName] = useState<string>("");
  const [error, setError] = useState<string | null>(null);
  const [isLoadingPath, setIsLoadingPath] = useState(false);
  const [path, setPath] = useState(exampleName);
  const [filter, setFilter] = useState<Filter>("all");
  const [query, setQuery] = useState("");

  const filteredEvents = useMemo(() => {
    if (!transcript) return [];

    const normalizedQuery = query.trim().toLowerCase();

    return transcript.events.filter((event) => {
      const filterMatch =
        filter === "all" ||
        (filter === "messages" &&
          ["text", "thinking", "redacted_thinking", "assistant", "user"].includes(event.kind)) ||
        (filter === "tools" && (event.kind === "tool_use" || event.kind === "tool_result")) ||
        (filter === "results" && event.type === "result") ||
        (filter === "errors" && event.isError);

      if (!filterMatch) return false;
      if (!normalizedQuery) return true;

      return [
        event.title,
        event.preview,
        event.type,
        event.role,
        event.kind,
        event.model,
        event.provider,
        event.toolName,
        event.toolUseId,
        event.uuid
      ]
        .filter(Boolean)
        .join(" ")
        .toLowerCase()
        .includes(normalizedQuery);
    });
  }, [filter, query, transcript]);

  function parseAndLoad(text: string, name: string) {
    try {
      const parsed = parseTranscriptSource(text);
      setTranscript(parsed);
      setFileName(name);
      setError(null);
      setFilter("all");
      setQuery("");
    } catch (parseError) {
      setTranscript(null);
      setFileName(name);
      setError(parseError instanceof Error ? parseError.message : String(parseError));
    }
  }

  async function loadPath(nextPath = path) {
    setIsLoadingPath(true);
    setError(null);

    try {
      const response = await fetch("/api/read-file", {
        method: "POST",
        headers: {
          "content-type": "application/json"
        },
        body: JSON.stringify({ path: nextPath }),
        cache: "no-store"
      });

      if (!response.ok) {
        const body = await response.json().catch(() => null) as {
          error?: string;
          details?: string;
        } | null;
        throw new Error(body?.details ?? body?.error ?? `File request failed with ${response.status}`);
      }

      const resolvedPath = response.headers.get("x-source-path") ?? nextPath;
      parseAndLoad(await response.text(), resolvedPath);
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : String(loadError));
    } finally {
      setIsLoadingPath(false);
    }
  }

  return (
    <main className="app-shell">
      <section className="path-band">
        <div className="brand-lockup" aria-label="Transcript inspector">
          <div className="brand-mark" aria-hidden="true">
            <span />
            <span />
            <span />
          </div>
          <div>
            <p className="eyebrow">ACP/X JSONL Viewer</p>
            <h1>Transcript logs, parsed into signal.</h1>
          </div>
        </div>

        <form
          className="path-form"
          onSubmit={(event) => {
            event.preventDefault();
            void loadPath();
          }}
        >
          <label>
            <span>Path to JSON or JSONL</span>
            <input
              type="text"
              value={path}
              onChange={(event) => setPath(event.target.value)}
              placeholder="/absolute/path/to/transcript.jsonl or ./transcript.json"
              spellCheck={false}
            />
          </label>
          <button className="primary-button" type="submit">
            {isLoadingPath ? "Parsing..." : "Parse path"}
          </button>
          <button
            className="secondary-button"
            type="button"
            onClick={() => {
              setPath(exampleName);
              void loadPath(exampleName);
            }}
          >
            Load sample
          </button>
        </form>

        <p className="path-copy">
          Enter a `.jsonl` or `.json` path on this machine. Claude Code event logs, ACP-style
          message arrays, tool results, and trailing usage records are handled directly.
        </p>
      </section>

      {error ? <p className="error-banner">{error}</p> : null}

      {transcript ? (
        <>
          <section className="summary-band">
            <div className="loaded-file">
              <span>Loaded</span>
              <strong title={fileName}>{fileName}</strong>
            </div>
            <div className="stat-grid">
              <Stat label="Events" value={formatNumber(transcript.summary.totalEvents)} />
              <Stat
                label="Turns"
                value={formatNumber(transcript.summary.numTurns ?? transcript.summary.turns.length)}
              />
              <Stat label="Cost" value={formatCost(transcript.summary.costUsd)} />
              <Stat label="Duration" value={formatDuration(transcript.summary.durationMs)} />
              <Stat
                label="Final input"
                value={formatNumber(transcript.summary.finalUsage?.inputTokens)}
              />
              <Stat
                label="Final output"
                value={formatNumber(transcript.summary.finalUsage?.outputTokens)}
              />
            </div>
          </section>

          <section className="context-strip" aria-label="Transcript context">
            <ContextItem label="Session" value={transcript.summary.sessionId} />
            <ContextItem label="Model" value={transcript.summary.model} />
            <ContextItem label="Provider" value={transcript.summary.provider} />
            <ContextItem label="Working directory" value={transcript.summary.cwd} wide />
          </section>

          <section className="workspace">
            <aside className="side-panel">
              <h2>Breakdown</h2>
              <KeyValueList values={transcript.summary.countsByType} />
              <h2>Event Kinds</h2>
              <KeyValueList values={transcript.summary.countsByKind} />
              <h2>Tools</h2>
              <KeyValueList values={transcript.summary.toolCounts} empty="No tool calls found." />
              <h2>Turns</h2>
              <TurnNavigation turns={transcript.summary.turns} />
            </aside>

            <section className="event-panel">
              <div className="toolbar">
                <label>
                  <span>Search</span>
                  <input
                    type="search"
                    value={query}
                    onChange={(event) => setQuery(event.target.value)}
                    placeholder="Command, model, uuid, text"
                  />
                </label>
                <label>
                  <span>Filter</span>
                  <select value={filter} onChange={(event) => setFilter(event.target.value as Filter)}>
                    <option value="all">All events</option>
                    <option value="messages">Messages</option>
                    <option value="tools">Tool flow</option>
                    <option value="results">Results</option>
                    <option value="errors">Errors</option>
                  </select>
                </label>
              </div>

              <div className="event-count">
                Showing {formatNumber(filteredEvents.length)} of{" "}
                {formatNumber(transcript.summary.totalEvents)}
              </div>

              <div className="event-list">
                {filteredEvents.map((event) => (
                  <EventRow key={`${event.line}-${event.uuid ?? event.kind}`} event={event} />
                ))}
              </div>
            </section>
          </section>
        </>
      ) : (
        <section className="empty-state">
          <h2>Start with a transcript.</h2>
          <p>
            Use the sample button to load the geophysics conversation from disk, or enter a JSON
            or JSONL transcript path.
          </p>
        </section>
      )}
    </main>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="stat-card">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function ContextItem({
  label,
  value,
  wide = false
}: {
  label: string;
  value: string | null;
  wide?: boolean;
}) {
  return (
    <div className={wide ? "context-item wide" : "context-item"}>
      <span>{label}</span>
      <strong title={value ?? undefined}>{value ?? "-"}</strong>
    </div>
  );
}

function KeyValueList({
  values,
  empty = "None"
}: {
  values: Record<string, number>;
  empty?: string;
}) {
  const entries = Object.entries(values).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]));

  if (!entries.length) return <p className="muted">{empty}</p>;

  return (
    <dl className="key-value-list">
      {entries.map(([key, value]) => (
        <div key={key}>
          <dt>{key}</dt>
          <dd>{formatNumber(value)}</dd>
        </div>
      ))}
    </dl>
  );
}

function TurnNavigation({ turns }: { turns: TranscriptTurn[] }) {
  if (!turns.length) return <p className="muted">No turns found.</p>;

  return (
    <nav className="turn-nav" aria-label="Turn navigation">
      {turns.map((turn) => (
        <a
          key={turn.index}
          className={turn.isError ? "turn-link has-error" : "turn-link"}
          href={`#event-${turn.firstEventIndex}`}
        >
          <span className="turn-link-top">
            <strong>Turn {turn.index}</strong>
            <span>Line {turn.line}</span>
          </span>
          <span className="turn-link-preview">{turn.preview || "No preview"}</span>
          <span className="turn-link-meta">
            {formatNumber(turn.eventCount)} events
            {turn.toolCount ? ` | ${formatNumber(turn.toolCount)} tools` : ""}
            {turn.inputTokens != null || turn.outputTokens != null
              ? ` | ${formatNumber(turn.inputTokens)} in / ${formatNumber(turn.outputTokens)} out`
              : ` | ${formatNumber(turn.roughTokens)} est.`}
          </span>
        </a>
      ))}
    </nav>
  );
}

function EventRow({ event }: { event: ParsedEvent }) {
  const [expanded, setExpanded] = useState(false);
  const raw = useMemo(() => JSON.stringify(event.record, null, 2), [event.record]);

  return (
    <article
      id={`event-${event.index}`}
      className={`event-row ${event.isError ? "has-error" : ""} ${
        expanded ? "is-expanded" : "is-collapsed"
      }`}
    >
      <div className="event-topline">
        <span className={`type-pill type-${safeClass(event.type)}`}>{event.type}</span>
        {event.turnIndex ? <span className="line-number">Turn {event.turnIndex}</span> : null}
        <span className="line-number">Line {event.line}</span>
        <strong>{event.title}</strong>
        <button
          className="compact-button"
          type="button"
          aria-expanded={expanded}
          onClick={() => setExpanded((current) => !current)}
        >
          {expanded ? "Collapse" : "Expand"}
        </button>
      </div>
      <p>{event.preview || "No text preview available."}</p>
      <div className="event-meta">
        <span>{event.kind}</span>
        <span>{event.role}</span>
        {event.toolName ? <span>{event.toolName}</span> : null}
        {event.messageId ? <span title={event.messageId}>Message {shortId(event.messageId)}</span> : null}
        {event.toolUseId ? <span title={event.toolUseId}>Tool id {shortId(event.toolUseId)}</span> : null}
      </div>
      <UsagePills usage={event.usage} roughTokens={event.roughTokens} />
      {expanded ? (
        <div className="event-expanded">
          <div className="event-sticky-actions">
            <span>{event.title}</span>
            <button className="compact-button" type="button" onClick={() => setExpanded(false)}>
              Collapse
            </button>
          </div>
          <MessageContent event={event} />
          <details>
            <summary>Raw JSON</summary>
            <pre>{raw}</pre>
          </details>
          <button
            className="bottom-collapse compact-button"
            type="button"
            onClick={() => setExpanded(false)}
          >
            Collapse message
          </button>
        </div>
      ) : null}
    </article>
  );
}

function UsagePills({
  usage,
  roughTokens
}: {
  usage: UsageSummary;
  roughTokens: number;
}) {
  const hasUsage = Object.values(usage).some((value) => typeof value === "number");

  return (
    <div className="usage-row" aria-label="Token usage">
      {hasUsage ? (
        <>
          <span>{formatNumber(usage.inputTokens)} input</span>
          <span>{formatNumber(usage.outputTokens)} output</span>
          <span>{formatNumber(usage.cacheReadInputTokens)} cache read</span>
          <span>{formatNumber(usage.cacheCreationInputTokens)} cache write</span>
          {usage.costUsd != null ? <span>{formatCost(usage.costUsd)}</span> : null}
        </>
      ) : null}
      <span>{formatNumber(roughTokens)} estimated tokens</span>
    </div>
  );
}

function MessageContent({ event }: { event: ParsedEvent }) {
  const message = asObject(event.record.message);
  const content = message?.content;

  if (typeof content === "string") {
    return (
      <section className="content-section">
        <h3>Message</h3>
        <pre className="content-pre">{content}</pre>
      </section>
    );
  }

  if (Array.isArray(content) && content.length) {
    return (
      <section className="content-section">
        <h3>Message blocks</h3>
        <div className="content-blocks">
          {content.map((block, index) => (
            <ContentBlock key={index} block={block} index={index} />
          ))}
        </div>
      </section>
    );
  }

  return (
    <section className="content-section">
      <h3>Record</h3>
      <pre className="content-pre">{JSON.stringify(event.record, null, 2)}</pre>
    </section>
  );
}

function ContentBlock({ block, index }: { block: unknown; index: number }) {
  const object = asObject(block);
  const type = typeof object?.type === "string" ? object.type : "block";

  if (!object) {
    return (
      <article className="content-block">
        <h4>Block {index + 1}</h4>
        <pre className="content-pre">{String(block)}</pre>
      </article>
    );
  }

  if (type === "tool_use") {
    const name = typeof object.name === "string" ? object.name : "tool";

    return (
      <article className="content-block">
        <h4>Tool call: {name}</h4>
        <pre className="content-pre">{JSON.stringify(object.input ?? object, null, 2)}</pre>
      </article>
    );
  }

  if (type === "tool_result") {
    return (
      <article className="content-block">
        <h4>Tool result</h4>
        <pre className="content-pre">{String(object.content ?? JSON.stringify(object, null, 2))}</pre>
      </article>
    );
  }

  if (type === "text" || type === "thinking") {
    const text = type === "text" ? object.text : object.thinking;

    return (
      <article className="content-block">
        <h4>{type === "text" ? "Text" : "Reasoning"}</h4>
        <pre className="content-pre">{String(text ?? "")}</pre>
      </article>
    );
  }

  if (type === "redacted_thinking") {
    const data = typeof object.data === "string" ? object.data : "";

    return (
      <article className="content-block">
        <h4>Redacted reasoning</h4>
        <p className="muted">
          Redacted payload{data ? `, ${formatNumber(data.length)} characters` : ""}.
        </p>
      </article>
    );
  }

  return (
    <article className="content-block">
      <h4>{titleCase(type)}</h4>
      <pre className="content-pre">{JSON.stringify(object, null, 2)}</pre>
    </article>
  );
}

function asObject(value: unknown): Record<string, unknown> | null {
  return typeof value === "object" && value !== null && !Array.isArray(value)
    ? value as Record<string, unknown>
    : null;
}

function shortId(value: string) {
  return value.length > 12 ? `${value.slice(0, 12)}...` : value;
}

function titleCase(value: string) {
  return value ? value.charAt(0).toUpperCase() + value.slice(1) : value;
}

function safeClass(value: string) {
  return value.replace(/[^a-z0-9_-]/gi, "").toLowerCase() || "unknown";
}
