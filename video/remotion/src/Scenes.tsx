/**
 * Scenes.tsx — animované vrstvy medzi footage zábermi (PVF v2).
 *
 * Cieľ: aby video nebolo len sekvencia záberov. Polovica plochy môže byť
 * animovaný panel, cez zábery lietajú emoji, cena sa odpočítava veľkým
 * minimalistickým číslom, CTA pristane na obrazovku s rozostrením pozadia.
 *
 * Všetko je deterministické (remotion `random(seed)`) — inak by každý render
 * vyzeral inak a Remotion by nevedel renderovať snímky paralelne.
 */
import React from "react";
import {
  AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig,
  random, Easing,
} from "remotion";
import { loadFont } from "@remotion/google-fonts/Montserrat";

const { fontFamily } = loadFont("normal", { weights: ["600", "800", "900"] });

const money = (n: number, decimals = 2) => n.toFixed(decimals).replace(".", ",");

/* ─────────── Lietajúce emoji ─────────── */

export type EmojiRain = {
  chars: string[];
  count?: number;
  seed?: string;
  size?: number;
  /** "up" = stúpajú ako bublinky, "burst" = vystrelia zo stredu */
  mode?: "up" | "burst";
};

export const FloatingEmojis: React.FC<{ cfg: EmojiRain; durationInFrames: number }> = ({
  cfg, durationInFrames,
}) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const n = cfg.count ?? 12;
  const seed = cfg.seed ?? "e";
  const size = cfg.size ?? 64;
  const mode = cfg.mode ?? "up";

  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      {new Array(n).fill(0).map((_, i) => {
        const r1 = random(`${seed}-${i}-x`);
        const r2 = random(`${seed}-${i}-d`);
        const r3 = random(`${seed}-${i}-s`);
        const char = cfg.chars[i % cfg.chars.length];

        // každý emoji štartuje inokedy, aby nešli v zástupe
        const delay = Math.floor(r2 * durationInFrames * 0.55);
        const life = durationInFrames - delay;
        const t = (frame - delay) / Math.max(1, life);
        if (t < 0 || t > 1) return null;

        const scale = 0.7 + r3 * 0.6;
        const fade = interpolate(t, [0, 0.12, 0.75, 1], [0, 1, 1, 0], {
          extrapolateLeft: "clamp", extrapolateRight: "clamp",
        });

        let x: number, y: number, rot: number;
        if (mode === "burst") {
          const ang = r1 * Math.PI * 2;
          const dist = interpolate(t, [0, 1], [0, 320 + r3 * 260], {
            easing: Easing.out(Easing.cubic),
          });
          x = width / 2 + Math.cos(ang) * dist;
          y = height / 2 + Math.sin(ang) * dist;
          rot = interpolate(t, [0, 1], [0, (r1 - 0.5) * 220]);
        } else {
          x = r1 * width;
          y = interpolate(t, [0, 1], [height * 1.05, -size]);
          // bočné hojdanie, aby nešli po priamke
          x += Math.sin((frame / fps) * (1.6 + r3) + r1 * 6) * 46;
          rot = Math.sin((frame / fps) * 2 + r1 * 6) * 18;
        }

        return (
          <div key={i} style={{
            position: "absolute", left: 0, top: 0,
            transform: `translate(${x - size / 2}px, ${y - size / 2}px) scale(${scale}) rotate(${rot}deg)`,
            fontSize: size, opacity: fade, lineHeight: 1,
            filter: "drop-shadow(0 4px 10px rgba(0,0,0,.28))",
          }}>{char}</div>
        );
      })}
    </AbsoluteFill>
  );
};

/* ─────────── Veľké minimalistické počítadlo ─────────── */

export type CounterCfg = {
  from: number;
  to: number;
  unit?: string;
  decimals?: number;
  label?: string;
  color?: string;
  bg?: string;
};

export const BigCounter: React.FC<{ cfg: CounterCfg; durationInFrames: number }> = ({
  cfg, durationInFrames,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const decimals = cfg.decimals ?? 2;

  // číslo dobehne v prvých ~65 % scény, zvyšok nech stojí a dá sa prečítať
  const run = Math.max(1, Math.round(durationInFrames * 0.65));
  const val = interpolate(frame, [0, run], [cfg.from, cfg.to], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

  const pop = spring({ frame, fps, config: { damping: 12, mass: 0.6 } });
  const settle = spring({
    frame: frame - run, fps, config: { damping: 9, mass: 0.5 },
  });
  const scale = 0.82 + pop * 0.18 + (frame > run ? settle * 0.07 : 0);

  return (
    <AbsoluteFill style={{
      justifyContent: "center", alignItems: "center", fontFamily,
      background: cfg.bg ?? "transparent",
    }}>
      {cfg.label ? (
        <div style={{
          fontSize: 40, fontWeight: 700, letterSpacing: 2,
          color: cfg.color ?? "#fff", opacity: 0.72,
          textTransform: "uppercase", marginBottom: 6,
          transform: `translateY(${interpolate(pop, [0, 1], [24, 0])}px)`,
        }}>{cfg.label}</div>
      ) : null}

      <div style={{
        fontSize: 210, fontWeight: 900, lineHeight: 0.92,
        color: cfg.color ?? "#fff",
        transform: `scale(${scale})`,
        letterSpacing: -6,
        fontVariantNumeric: "tabular-nums",   // číslice neposkakujú do strán
      }}>{money(val, decimals)}</div>

      {cfg.unit ? (
        <div style={{
          fontSize: 46, fontWeight: 800, color: cfg.color ?? "#fff",
          opacity: 0.9, marginTop: 4,
        }}>{cfg.unit}</div>
      ) : null}
    </AbsoluteFill>
  );
};

/* ─────────── Animovaný panel (do polovice obrazovky) ─────────── */

export type PanelCfg = {
  kind: "counter" | "bullets" | "headline";
  bg?: string;
  color?: string;
  accent?: string;
  counter?: CounterCfg;
  bullets?: string[];
  headline?: string;
  sub?: string;
};

export const Panel: React.FC<{ cfg: PanelCfg; durationInFrames: number }> = ({
  cfg, durationInFrames,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const color = cfg.color ?? "#ffffff";

  return (
    <AbsoluteFill style={{
      background: cfg.bg ?? "#13161D", fontFamily,
      justifyContent: "center", alignItems: "center", padding: 44,
    }}>
      {cfg.kind === "counter" && cfg.counter ? (
        <BigCounter cfg={{ ...cfg.counter, color }} durationInFrames={durationInFrames} />
      ) : null}

      {cfg.kind === "bullets" && cfg.bullets ? (
        <div style={{ width: "100%" }}>
          {cfg.bullets.map((b, i) => {
            // Nábeh musí byť rýchly — text treba stihnúť prečítať.
            // Pri stagger 6f bol posledný riadok vonku až po 0,4 s.
            const s = spring({
              frame: frame - i * 3, fps, config: { damping: 16, mass: 0.5 },
            });
            return (
              <div key={i} style={{
                display: "flex", alignItems: "center", gap: 24, marginBottom: 34,
                opacity: s,
                transform: `translateX(${interpolate(s, [0, 1], [-50, 0])}px)`,
              }}>
                <div style={{
                  width: 22, height: 22, borderRadius: 11,
                  background: cfg.accent ?? "#4F52F7", flexShrink: 0,
                  transform: `scale(${s})`,
                }} />
                <div style={{ fontSize: 66, fontWeight: 800, color, lineHeight: 1.14 }}>{b}</div>
              </div>
            );
          })}
        </div>
      ) : null}

      {cfg.kind === "headline" ? (
        <div style={{ textAlign: "center" }}>
          <div style={{
            fontSize: 76, fontWeight: 900, color, lineHeight: 1.05,
            transform: `scale(${spring({ frame, fps, config: { damping: 13 } })})`,
          }}>{cfg.headline}</div>
          {cfg.sub ? (
            <div style={{
              fontSize: 40, fontWeight: 700, color, opacity: 0.75, marginTop: 18,
              transform: `translateY(${interpolate(
                spring({ frame: frame - 7, fps, config: { damping: 15 } }), [0, 1], [30, 0])}px)`,
            }}>{cfg.sub}</div>
          ) : null}
        </div>
      ) : null}
    </AbsoluteFill>
  );
};

/* ─────────── CTA, ktoré pristane + rozostrí pozadie ─────────── */

export type CtaCfg = {
  text: string;
  bg?: string;
  color?: string;
  /** snímka (v rámci celého videa), kedy CTA pristane */
  landFrame: number;
  /** Odkiaľ priletí. "right"/"left" neprekrýva titulky, "top" áno. */
  from?: "right" | "left" | "top";
  /** odsadenie zdola (podiel výšky). Default 0.13; safezone (RULES #15) = 0.22 */
  bottomPct?: number;
};

export const CtaLanding: React.FC<{ cfg: CtaCfg; noBlur?: boolean }> = ({ cfg, noBlur }) => {
  const frame = useCurrentFrame();
  const { fps, height, width } = useVideoConfig();
  const f = frame - cfg.landFrame;
  if (f < -12) return null;

  // Priletí z boku (default) — zhora by preletel cez titulky.
  const dir = cfg.from ?? "right";
  const land = spring({ frame: f, fps, config: { damping: 13, mass: 0.9, stiffness: 120 } });
  const fromTop = dir === "top";
  const off = dir === "left" ? -width : width;
  const x = fromTop ? 0 : interpolate(land, [0, 1], [off, 0]);
  const y = fromTop ? interpolate(land, [0, 1], [-320, 0]) : 0;
  // pri prílete z boku sa stlačí vodorovne, nie zvisle
  const squash = interpolate(land, [0, 0.72, 0.88, 1], [1.12, 0.94, 1.04, 1], {
    extrapolateRight: "clamp",
  });

  // nárazová vlna rozostrenia v momente dosadnutia
  const impact = interpolate(f, [8, 14, 30], [0, 1, 0], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp",
  });

  // jemné dýchanie po dosadnutí, nech to nezamrzne
  const pulse = f > 26 ? 1 + Math.sin((f - 26) / fps * 4.2) * 0.022 : 1;

  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      {/* rozostrenie a stmavenie pozadia pri dopade */}
      {impact > 0.01 ? (
        <AbsoluteFill style={{
          ...(noBlur ? {} : {
            backdropFilter: `blur(${impact * 16}px)`,
            WebkitBackdropFilter: `blur(${impact * 16}px)`,
          }),
          background: `rgba(0,0,0,${impact * 0.22})`,
        }} />
      ) : null}

      <AbsoluteFill style={{
        justifyContent: "flex-end", alignItems: "center",
        paddingBottom: Math.round(height * (cfg.bottomPct ?? 0.13)), fontFamily,
      }}>
        <div style={{
          transform: `translate(${x}px, ${y}px) ${fromTop ? `scaleY(${squash})` : `scaleX(${squash})`} scale(${pulse})`,
          background: cfg.bg ?? "#4F52F7",
          color: cfg.color ?? "#fff",
          fontSize: 62, fontWeight: 900, letterSpacing: 1,
          padding: "30px 62px", borderRadius: 999,
          boxShadow: `0 ${18 + impact * 26}px ${44 + impact * 40}px rgba(0,0,0,${0.32 + impact * 0.2})`,
          whiteSpace: "nowrap",
        }}>{cfg.text}</div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
