import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  spring,
  interpolate,
  Easing,
} from "remotion";
import { loadFont } from "@remotion/google-fonts/Montserrat";

const { fontFamily } = loadFont("normal", { weights: ["600", "800", "900"] });

export type Word = { word: string; start: number; end: number; eos?: boolean };

export type TopCard =
  | { kind: "price_count"; from: number; to: number; unit: string; decimals?: number; start: number; end: number }
  | { kind: "text"; text: string; start: number; end: number }
  | { kind: "benefits"; items: string[]; start: number; end: number }
  | { kind: "social"; text: string; start: number; end: number };

// Vizuálna téma videa — mení farby a štýly, aby nevyzeralo každé video rovnako.
export type Theme = {
  accent: string;          // hlavný akcent (aktívne slovo, cenovka, CTA)
  accent2: string;         // sekundárny akcent (hviezdy, detaily)
  onAccent: string;        // farba textu NA accent-pozadí (cenovka)
  captionColor: string;    // farba neaktívneho slova titulku
  captionStyle: "outline" | "block";  // outline = čierny obrys; block = text v boxe
  captionBg: string;       // pozadie block-titulku / farba obrysu
  ctaStyle: "pill" | "bar" | "ticket";
  ctaBg: string;
  ctaColor: string;
  cardBg: string;          // pozadie horných kariet
  cardColor: string;       // text horných kariet
  cardStyle: "pill" | "boxed" | "minimal";
  captionPos: number;      // y pozícia titulkov (0.5 = stred)
};

const DEFAULT_THEME: Theme = {
  accent: "#4F52F7", accent2: "#ffd400", onAccent: "#ffffff",
  captionColor: "#ffffff", captionStyle: "outline", captionBg: "#000000",
  ctaStyle: "pill", ctaBg: "#4F52F7", ctaColor: "#ffffff",
  cardBg: "#13161D", cardColor: "#ffffff", cardStyle: "pill",
  captionPos: 0.5,
};

export type CaptionProps = {
  words: Word[];
  fps: number;
  width: number;
  height: number;
  highlight_color: string;
  primary_color: string;
  font_size: number;
  y_position: number;
  brand?: string;
  topCards?: TopCard[];
  cta?: { text: string; start: number };
  transitions?: number[];
  theme?: Theme;
  /** Vypne backdrop-filter blur na titulkovom boxe. Blur beží na každej snímke
   *  a je to hlavný podozrivý pri nekonzistentnom vykresľovaní. */
  noBackdropBlur?: boolean;
};

function groupWords(words: Word[], per = 3): Word[][] {
  // zoskupenie po `per` slov, ALE nikdy nespájame slová cez koniec vety (eos)
  const groups: Word[][] = [];
  let cur: Word[] = [];
  for (const w of words) {
    cur.push(w);
    if (cur.length >= per || w.eos) {
      groups.push(cur);
      cur = [];
    }
  }
  if (cur.length) groups.push(cur);
  return groups;
}

const OUT = "6px";
const STROKE = `-${OUT} 0 #000,${OUT} 0 #000,0 -${OUT} #000,0 ${OUT} #000,${OUT} ${OUT} #000,-${OUT} -${OUT} #000,${OUT} -${OUT} #000,-${OUT} ${OUT} #000`;

// desatinná čiarka podľa lokálu; Ft sa uvádza bez desatinných miest (decimals=0)
const money = (n: number, decimals = 2) => n.toFixed(decimals).replace(".", ",");

export const Captions: React.FC<CaptionProps> = (props) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const th = props.theme ?? DEFAULT_THEME;
  const t = frame / fps;
  const groups = groupWords(props.words, 3);

  let activeGroup: Word[] | null = null;
  let activeIdx = 0;
  for (const g of groups) {
    if (t >= g[0].start && t <= g[g.length - 1].end + 0.15) {
      activeGroup = g;
      activeIdx = 0;
      for (let j = 0; j < g.length; j++) {
        const wEnd = j + 1 < g.length ? g[j + 1].start : g[j].end;
        if (t >= g[j].start && t < wEnd) activeIdx = j;
      }
      if (t > g[g.length - 1].end) activeIdx = g.length - 1;
      break;
    }
  }

  const block = th.captionStyle === "block";
  const capTop = (th.captionPos ?? 0.5) * props.height;

  return (
    <AbsoluteFill style={{ fontFamily }}>
      {props.brand && <Brand text={props.brand} color={th.accent} fps={fps} />}

      {(props.topCards ?? []).map((c, i) =>
        t >= c.start && t <= c.end ? (
          <TopSlot key={i} card={c} props={props} th={th} fps={fps} />
        ) : null
      )}

      {/* ── Karaoke titulky ── */}
      {activeGroup && (
        <div
          style={{
            position: "absolute",
            top: capTop,
            left: 0,
            width: props.width,
            transform: "translateY(-50%)",
            display: "flex",
            justifyContent: "center",
            padding: "0 60px",
          }}
        >
          <div
            style={{
              display: "flex",
              flexWrap: "wrap",
              justifyContent: "center",
              gap: props.font_size * (block ? 0.38 : 0.5),
              ...(block
                ? {
                    background: th.captionBg,
                    ...(props.noBackdropBlur
                      ? {}
                      : { backdropFilter: "blur(10px)", WebkitBackdropFilter: "blur(10px)" }),
                    padding: `${props.font_size * 0.18}px ${props.font_size * 0.32}px`,
                    borderRadius: 24,
                  }
                : {}),
            }}
          >
            {activeGroup.map((w, j) => {
              const isActive = j === activeIdx;
              // ⚠️ Pop MUSÍ dobehnúť späť na 1.0.
              // Keď slovo ostane zväčšené a pri deaktivácii skočí z 1.08 na 1.0,
              // trhne o 8 % a tlačí susedné slová — pri karaoke sa to deje
              // pri každom slove a celý titulok viditeľne poskakuje.
              const since = frame - Math.round(w.start * fps);
              const scale = isActive
                ? interpolate(since, [0, 2, 7], [0.94, 1.05, 1.0], {
                    extrapolateLeft: "clamp",
                    extrapolateRight: "clamp",
                    easing: Easing.out(Easing.quad),
                  })
                : 1;
              return (
                <span
                  key={j}
                  style={{
                    fontSize: props.font_size,
                    fontWeight: 900,
                    letterSpacing: "-1px",
                    color: isActive ? th.accent : th.captionColor,
                    textShadow: block
                      ? (th.captionColor === "#ffffff" ? "0 2px 12px rgba(0,0,0,0.65)" : "0 1px 6px rgba(255,255,255,0.5)")
                      : STROKE,
                    transform: `scale(${scale})`,
                    transformOrigin: "center bottom",
                    display: "inline-block",
                    textTransform: "uppercase",
                  }}
                >
                  {w.word.replace(/\n/g, " ")}
                </span>
              );
            })}
          </div>
        </div>
      )}

      {props.cta && t >= props.cta.start && (
        <Cta text={props.cta.text} th={th} start={props.cta.start} fps={fps} height={props.height} width={props.width} />
      )}

      {(props.transitions ?? []).map((tt, i) => (
        <Wipe key={i} at={tt} color={th.accent} fps={fps} width={props.width} height={props.height} />
      ))}
    </AbsoluteFill>
  );
};

// ── Horný slot ──
const TopSlot: React.FC<{ card: TopCard; props: CaptionProps; th: Theme; fps: number }> = ({ card, props, th, fps }) => {
  const frame = useCurrentFrame();
  const localStart = Math.round(card.start * fps);
  const pop = spring({ frame: frame - localStart, fps, config: { damping: 12, mass: 0.6 } });
  const appear = interpolate(pop, [0, 1], [0, 1]);
  const y = interpolate(pop, [0, 1], [-40, 0]);
  const top = props.height * 0.15;

  const wrap = (children: React.ReactNode): React.ReactNode => (
    <div style={{ position: "absolute", top, left: 0, width: props.width, display: "flex", justifyContent: "center", opacity: appear, transform: `translateY(${y}px)` }}>
      {children}
    </div>
  );

  // štýl "obalu" karty podľa témy
  const cardBox = (extra: React.CSSProperties): React.CSSProperties => {
    const base: React.CSSProperties = { fontSize: 54, fontWeight: 800, padding: "16px 40px", ...extra };
    if (th.cardStyle === "minimal")
      return { ...base, background: th.cardBg, color: th.cardColor, borderRadius: 18, borderLeft: `6px solid ${th.accent}` };
    if (th.cardStyle === "boxed")
      return { ...base, background: th.cardBg, color: th.cardColor, borderRadius: 22, border: `3px solid ${th.accent}` };
    // pill
    return { ...base, background: th.cardBg, color: th.cardColor, borderRadius: 999, border: `3px solid ${th.accent}` };
  };

  if (card.kind === "price_count") {
    const p = interpolate(frame - localStart, [0, fps * 0.9], [card.from, card.to], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) });
    return wrap(
      <div style={{ background: th.accent, color: th.onAccent, fontSize: 58, fontWeight: 800, padding: "16px 42px", borderRadius: th.cardStyle === "pill" ? 999 : 20, boxShadow: `0 12px 40px ${th.accent}66` }}>
        {money(p, card.decimals)} {card.unit}
      </div>
    );
  }
  if (card.kind === "text") {
    return wrap(<div style={cardBox({})}>{card.text}</div>);
  }
  if (card.kind === "social") {
    const light = th.cardStyle === "boxed"; // cream téma má tmavý text
    return wrap(
      <div style={{ background: light ? "#ffffff" : "#ffffff", color: "#13161D", padding: "18px 34px", borderRadius: 28, boxShadow: "0 10px 34px rgba(0,0,0,0.3)", display: "flex", flexDirection: "column", alignItems: "center", gap: 6, maxWidth: props.width * 0.82, textAlign: "center", border: `2px solid ${th.accent}` }}>
        <span style={{ color: th.accent2, fontSize: 44, letterSpacing: 4 }}>★★★★★</span>
        <span style={{ fontSize: 40, fontWeight: 800, lineHeight: 1.15 }}>{card.text}</span>
      </div>
    );
  }
  // benefits
  return (
    <div style={{ position: "absolute", top, left: 0, width: props.width, display: "flex", flexDirection: "column", alignItems: "center", gap: 16, opacity: appear }}>
      {card.items.map((it, k) => {
        const bp = spring({ frame: frame - localStart - k * 8, fps, config: { damping: 13, mass: 0.6 } });
        const bo = interpolate(bp, [0, 1], [0, 1]);
        const bx = interpolate(bp, [0, 1], [60, 0]);
        return (
          <div key={k} style={{ opacity: bo, transform: `translateX(${bx}px)`, background: th.cardBg, color: th.cardColor, fontSize: 44, fontWeight: 700, padding: "12px 32px", borderRadius: th.cardStyle === "pill" ? 999 : 16, display: "flex", alignItems: "center", gap: 14, border: th.cardStyle === "minimal" ? "none" : `2px solid ${th.accent}55` }}>
            <span style={{ color: th.accent, fontSize: 40 }}>✓</span> {it}
          </div>
        );
      })}
    </div>
  );
};

const Brand: React.FC<{ text: string; color: string; fps: number }> = ({ text, color, fps }) => {
  const frame = useCurrentFrame();
  const pulse = 1 + Math.sin((frame / fps) * 2) * 0.03;
  const intro = spring({ frame, fps, config: { damping: 14 } });
  return (
    <div style={{ position: "absolute", top: 46, left: 48, opacity: interpolate(intro, [0, 1], [0, 1]), transform: `scale(${pulse})`, transformOrigin: "left center" }}>
      <span style={{ fontSize: 52, fontWeight: 900, fontStyle: "italic", color, textShadow: STROKE, letterSpacing: "1px" }}>{text}</span>
    </div>
  );
};

const Cta: React.FC<{ text: string; th: Theme; start: number; fps: number; height: number; width: number }> = ({ text, th, start, fps, height, width }) => {
  const frame = useCurrentFrame();
  const local = frame - Math.round(start * fps);
  const pop = spring({ frame: local, fps, config: { damping: 11, mass: 0.7 } });
  const pulse = 1 + Math.sin((local / fps) * 6) * 0.04;
  const appear = interpolate(pop, [0, 1], [0, 1]);

  if (th.ctaStyle === "bar") {
    // plný pásik cez celú šírku (v safezone, ~74 %)
    const yb = interpolate(pop, [0, 1], [80, 0]);
    return (
      <div style={{ position: "absolute", top: height * 0.74, left: 0, width, display: "flex", justifyContent: "center", opacity: appear, transform: `translateY(${yb}px)` }}>
        <div style={{ width: width * 0.92, background: th.ctaBg, color: th.ctaColor, fontSize: 50, fontWeight: 900, padding: "24px 0", borderRadius: 20, textTransform: "uppercase", letterSpacing: "1px", textAlign: "center", boxShadow: `0 14px 46px ${th.ctaBg}88` }}>
          {text}
        </div>
      </div>
    );
  }
  if (th.ctaStyle === "ticket") {
    const scale = interpolate(pop, [0, 1], [0.6, 1]);
    return (
      <div style={{ position: "absolute", top: height * 0.72, left: 0, width, display: "flex", justifyContent: "center", opacity: appear }}>
        <div style={{ transform: `scale(${scale})`, background: th.ctaBg, color: th.ctaColor, fontSize: 50, fontWeight: 900, padding: "20px 48px", borderRadius: 16, border: `4px dashed ${th.accent}`, textTransform: "uppercase", letterSpacing: "0.5px", textAlign: "center", maxWidth: width * 0.85 }}>
          {text}
        </div>
      </div>
    );
  }
  // pill (default, pulzujúci)
  const scale = interpolate(pop, [0, 1], [0.4, 1]) * pulse;
  return (
    <div style={{ position: "absolute", top: height * 0.72, left: 0, width, display: "flex", justifyContent: "center", opacity: appear }}>
      <div style={{ transform: `scale(${scale})`, background: th.ctaBg, color: th.ctaColor, fontSize: 50, fontWeight: 900, padding: "22px 54px", borderRadius: 999, boxShadow: `0 14px 46px ${th.ctaBg}99`, textTransform: "uppercase", letterSpacing: "0.5px", textAlign: "center", maxWidth: width * 0.85 }}>
        {text}
      </div>
    </div>
  );
};

const Wipe: React.FC<{ at: number; color: string; fps: number; width: number; height: number }> = ({ at, color, fps, width, height }) => {
  const frame = useCurrentFrame();
  const local = frame - Math.round(at * fps);
  const dur = Math.round(fps * 0.35);
  if (local < 0 || local > dur) return null;
  const p = local / dur;
  const x = interpolate(p, [0, 1], [-width * 1.6, width * 1.6], { easing: Easing.inOut(Easing.cubic) });
  return (
    <div style={{ position: "absolute", top: -height * 0.2, left: 0, width: width * 0.6, height: height * 1.4, background: color, transform: `translateX(${x}px) skewX(-16deg)`, opacity: 0.9 }} />
  );
};
