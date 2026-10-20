/**
 * Ad.tsx — CELÉ video v Remotion (PVF v2, "cesta B").
 *
 * Nahrádza ffmpeg reťaz normalize_clip -> concat -> overlay -> mux jedným renderom:
 *   footage klipy + prechody + Ken Burns + titulky + voiceover + hudba
 *
 * Titulkovú vrstvu NEDUPLIKUJE — znovupoužíva existujúci <Captions> komponent,
 * ktorý je odladený a schválený. Pribudla len footage vrstva pod ním.
 *
 * ⚠️ TransitionSeries SKRACUJE timeline o dĺžku prechodov. Kompenzáciu rieši
 * make_ad_props.py, ktorý dĺžky klipov dopredu nafúkne — pozri tam.
 */
import React from "react";
import {
  AbsoluteFill,
  Img,
  staticFile,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
  Easing,
  Sequence,
} from "remotion";
import { Video, Audio } from "@remotion/media";
import { TransitionSeries, linearTiming, springTiming } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { slide } from "@remotion/transitions/slide";
import { wipe } from "@remotion/transitions/wipe";
import { clockWipe } from "@remotion/transitions/clock-wipe";
import { iris } from "@remotion/transitions/iris";
import { dreamyZoom } from "@remotion/transitions/dreamy-zoom";
import { linearBlur } from "@remotion/transitions/linear-blur";
import { zoomBlur } from "@remotion/transitions/zoom-blur";
import { filmBurn } from "@remotion/transitions/film-burn";
import { crossZoom } from "@remotion/transitions/cross-zoom";
import { dissolve } from "@remotion/transitions/dissolve";
import { none } from "@remotion/transitions/none";
import { punch, flash } from "./Punch";
import { Captions, CaptionProps } from "./Captions";
import { FloatingEmojis, Panel, CtaLanding, EmojiRain, PanelCfg, CtaCfg } from "./Scenes";

export type KenMode = "in" | "out" | "left" | "right" | "up" | "none";

export type Clip = {
  src: string;                 // cesta v public/ (cez staticFile)
  kind: "video" | "image";
  durationInFrames: number;
  ken?: KenMode;
  trimBefore?: number;         // orez od začiatku zdroja, v snímkach
  playbackRate?: number;
  /** Ponechá zvuk klipu (intro má vlastný hovorený part). */
  keepAudio?: boolean;
  /** Rozloženie scény. "split-*" = footage zaberá časť plochy, zvyšok je animovaný panel. */
  layout?: "full" | "split-bottom" | "split-top";
  /** Koľko plochy zaberie footage pri split layoute (0–1). Default 0.58. */
  splitRatio?: number;
  panel?: PanelCfg;
  emojis?: EmojiRain;
  kenPhaseFrom?: number;
  kenPhaseTo?: number;
};

export type TransitionType =
  | "none" | "fade" | "punch" | "flash" | "dissolve" | "slide" | "wipe" | "clockWipe" | "iris"
  | "dreamyZoom" | "linearBlur" | "zoomBlur" | "filmBurn" | "crossZoom";

export type TransitionSpec = {
  type: TransitionType;
  durationInFrames: number;
  direction?: "from-left" | "from-right" | "from-top" | "from-bottom";
  spring?: boolean;
};

export type AdProps = {
  clips: Clip[];
  transitions: TransitionSpec[];   // dĺžka musí byť clips.length - 1
  captions: CaptionProps;
  fps: number;
  width: number;
  height: number;
  voice?: string;                  // public/ cesta k voiceoveru
  music?: string;                  // public/ cesta k hudbe
  musicVolume?: number;
  /** Snímka, od ktorej hrá hudba (za hookom, nech neprekrýva hovorené slovo). */
  musicFrom?: number;
  totalDurationInFrames: number;
  cta?: CtaCfg;
  noBackdropBlur?: boolean;
  /** Dĺžka intro klipu. Titulky a voiceover začínajú až za ním. */
  introFrames?: number;
};

/* ---------- Ken Burns ---------- */

const KEN: Record<KenMode, { s: [number, number]; x: [number, number]; y: [number, number] }> = {
  in:    { s: [1.0, 1.10], x: [0, 0],    y: [0, 0] },
  out:   { s: [1.10, 1.0], x: [0, 0],    y: [0, 0] },
  left:  { s: [1.08, 1.08], x: [2.5, -2.5], y: [0, 0] },
  right: { s: [1.08, 1.08], x: [-2.5, 2.5], y: [0, 0] },
  up:    { s: [1.08, 1.08], x: [0, 0],  y: [2.5, -2.5] },
  none:  { s: [1.0, 1.0],   x: [0, 0],  y: [0, 0] },
};

const KenBurns: React.FC<{
  mode: KenMode;
  durationInFrames: number;
  /** Odkiaľ-pokiaľ v krivke pohybu (0–1). Rozsekaný záber tak nadviaže
   *  tam, kde prvá polovica skončila — inak zoom na strihu viditeľne skočí. */
  phaseFrom?: number;
  phaseTo?: number;
  children: React.ReactNode;
}> = ({ mode, durationInFrames, phaseFrom = 0, phaseTo = 1, children }) => {
  const frame = useCurrentFrame();
  const k = KEN[mode] ?? KEN.none;
  const opts = {
    extrapolateLeft: "clamp" as const,
    extrapolateRight: "clamp" as const,
    easing: Easing.bezier(0.33, 0, 0.67, 1),   // jemný ease-in-out, bez švihu
  };
  const phase = interpolate(frame, [0, Math.max(1, durationInFrames)],
                            [phaseFrom, phaseTo], opts);
  const range: [number, number] = [0, 1];
  const scale = interpolate(phase, range, k.s, opts);
  const x = interpolate(phase, range, k.x, opts);
  const y = interpolate(phase, range, k.y, opts);

  return (
    <AbsoluteFill style={{ overflow: "hidden" }}>
      <AbsoluteFill style={{ transform: `scale(${scale}) translate(${x}%, ${y}%)` }}>
        {children}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

/* ---------- Prechody ---------- */

const presentationFor = (t: TransitionSpec, width: number, height: number) => {
  switch (t.type) {
    case "fade":       return fade();
    case "punch":      return punch();
    case "flash":      return flash();
    case "dissolve":   return dissolve();
    case "slide":      return slide({ direction: t.direction ?? "from-right" });
    case "wipe":       return wipe({ direction: t.direction ?? "from-right" });
    case "clockWipe":  return clockWipe({ width, height });
    case "iris":       return iris({ width, height });
    case "dreamyZoom": return dreamyZoom();
    case "linearBlur": return linearBlur();
    case "zoomBlur":   return zoomBlur();
    case "filmBurn":   return filmBurn();
    case "crossZoom":  return crossZoom();
    default:           return none();
  }
};

const timingFor = (t: TransitionSpec) =>
  t.spring
    ? springTiming({ config: { damping: 200 }, durationInFrames: t.durationInFrames })
    : linearTiming({ durationInFrames: t.durationInFrames });

/* ---------- Footage vrstva ---------- */

const ClipContent: React.FC<{ clip: Clip }> = ({ clip }) => {
  const style: React.CSSProperties = {
    width: "100%",
    height: "100%",
    objectFit: "cover",
  };
  if (clip.kind === "image") {
    return <Img src={staticFile(clip.src)} style={style} />;
  }
  return (
    <Video
      src={staticFile(clip.src)}
      style={style}
      muted={!clip.keepAudio}       // zvuk footage nechceme, ide VO (výnimka: intro)
      trimBefore={clip.trimBefore}
      playbackRate={clip.playbackRate}
      objectFit="cover"
    />
  );
};

/** Jedna scéna: footage (celá plocha alebo polovica) + voliteľný panel + emoji. */
const Scene: React.FC<{ clip: Clip }> = ({ clip }) => {
  const layout = clip.layout ?? "full";
  const ratio = clip.splitRatio ?? 0.58;
  const d = clip.durationInFrames;

  const footage = (
    <KenBurns
      mode={clip.ken ?? "none"}
      durationInFrames={d}
      phaseFrom={clip.kenPhaseFrom}
      phaseTo={clip.kenPhaseTo}
    >
      <ClipContent clip={clip} />
    </KenBurns>
  );

  if (layout === "full" || !clip.panel) {
    return (
      <AbsoluteFill>
        {footage}
        {clip.emojis ? <FloatingEmojis cfg={clip.emojis} durationInFrames={d} /> : null}
      </AbsoluteFill>
    );
  }

  const footageFirst = layout === "split-top";
  const fPct = `${ratio * 100}%`;
  const pPct = `${(1 - ratio) * 100}%`;

  return (
    <AbsoluteFill style={{ display: "flex", flexDirection: "column" }}>
      <div style={{ position: "relative", height: footageFirst ? fPct : pPct, overflow: "hidden" }}>
        {footageFirst ? footage : <Panel cfg={clip.panel} durationInFrames={d} />}
      </div>
      <div style={{ position: "relative", height: footageFirst ? pPct : fPct, overflow: "hidden" }}>
        {footageFirst ? <Panel cfg={clip.panel} durationInFrames={d} /> : footage}
      </div>
      {clip.emojis ? <FloatingEmojis cfg={clip.emojis} durationInFrames={d} /> : null}
    </AbsoluteFill>
  );
};

const Footage: React.FC<{ props: AdProps }> = ({ props }) => {
  const { clips, transitions, width, height } = props;
  return (
    <TransitionSeries>
      {clips.map((clip, i) => {
        const tr = transitions[i - 1];
        return (
          <React.Fragment key={i}>
            {i > 0 && tr && tr.type !== "none" ? (
              <TransitionSeries.Transition
                presentation={presentationFor(tr, width, height)}
                timing={timingFor(tr)}
              />
            ) : null}
            <TransitionSeries.Sequence durationInFrames={clip.durationInFrames}>
              <Scene clip={clip} />
            </TransitionSeries.Sequence>
          </React.Fragment>
        );
      })}
    </TransitionSeries>
  );
};

/* ---------- Kompozícia ---------- */

export const Ad: React.FC<AdProps> = (props) => {
  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      <Footage props={props} />

      {/* Titulky + karty — existujúci odladený komponent.
          Sequence posunie ich vnútorný čas za intro, takže časovanie slov
          netreba prepočítavať. */}
      <Sequence from={props.introFrames ?? 0}>
        <AbsoluteFill>
          <Captions {...props.captions} noBackdropBlur={props.noBackdropBlur} />
        </AbsoluteFill>
      </Sequence>

      {props.cta ? <CtaLanding cfg={props.cta} noBlur={props.noBackdropBlur} /> : null}

      {props.voice ? (
        <Sequence from={props.introFrames ?? 0}>
          <Audio src={staticFile(props.voice)} />
        </Sequence>
      ) : null}

      {props.music ? (
        <Sequence from={props.musicFrom ?? 0}>
          <Audio
            src={staticFile(props.music)}
            // plynulý nábeh cez ~1 s, nech hudba nenaskočí naraz
            volume={(f) =>
              interpolate(f, [0, 30], [0, props.musicVolume ?? 0.07], {
                extrapolateLeft: "clamp",
                extrapolateRight: "clamp",
              })
            }
            loop
          />
        </Sequence>
      ) : null}
    </AbsoluteFill>
  );
};
