import { Composition } from "remotion";
import { Captions, CaptionProps } from "./Captions";
import { FlashPhoto, FlashPhotoProps } from "./FlashPhoto";
import { Ad, AdProps } from "./Ad";

// Statická UGC fotka + animované info karty (flash ponuka). Nezávislé od video pipeline.
const flashDefaults: FlashPhotoProps = {
  image: "ugc-flash.png",
  fps: 30,
  width: 1080,
  height: 1920,
  durationSec: 10,
  headline: "PRODUKT + DARČEK",
  freeWord: "ZADARMO",
  bullets: ["Doprava zdarma", "Len 0,99 € za použitie", "Ponuka platí obmedzený čas"],
  priceFrom: 79.97,
  priceTo: 32.99,
  currency: "€",
  discount: "-58 %",
  cta: "CHCEM TO",
};

// Default props — prepíšu sa cez --props=props.json pri renderi.
const defaultProps: CaptionProps = {
  words: [
    { word: "Brand", start: 0, end: 0.5 },
    { word: "nový", start: 0.5, end: 1.0 },
    { word: "štýl", start: 1.0, end: 1.7 },
  ],
  fps: 30,
  width: 1080,
  height: 1920,
  highlight_color: "#4F52F7",
  primary_color: "#ffffff",
  font_size: 88,
  y_position: 0.5,
  price_label: "0,99 €/ks",
};

// Dĺžka podľa posledného slova + 0.15s buffer (rovnako ako PIL pipeline).
const calcFrames = (p: CaptionProps) => {
  const lastEnd = p.words.length ? p.words[p.words.length - 1].end : 1;
  return Math.ceil((lastEnd + 0.15) * p.fps);
};

export const RemotionRoot: React.FC = () => {
  return (
    <>
    <Composition
      id="Captions"
      component={Captions}
      durationInFrames={calcFrames(defaultProps)}
      fps={defaultProps.fps}
      width={defaultProps.width}
      height={defaultProps.height}
      defaultProps={defaultProps}
      calculateMetadata={({ props }) => ({
        durationInFrames: calcFrames(props),
        fps: props.fps,
        width: props.width,
        height: props.height,
      })}
    />

    <Composition
      id="FlashPhoto"
      component={FlashPhoto}
      durationInFrames={flashDefaults.durationSec * flashDefaults.fps}
      fps={flashDefaults.fps}
      width={flashDefaults.width}
      height={flashDefaults.height}
      defaultProps={flashDefaults}
      calculateMetadata={({ props }) => ({
        durationInFrames: Math.round(props.durationSec * props.fps),
        fps: props.fps,
        width: props.width,
        height: props.height,
      })}
    />
    {/* Celé video v Remotion (cesta B) — footage + prechody + Ken Burns + titulky + audio.
        Props generuje scripts/make_ad_props.py, ktorý rieši aj kompenzáciu
        skrátenia timeline prechodmi. */}
    <Composition
      id="Ad"
      component={Ad}
      durationInFrames={300}
      fps={30}
      width={1080}
      height={1920}
      defaultProps={{
        clips: [],
        transitions: [],
        captions: defaultProps,
        fps: 30,
        width: 1080,
        height: 1920,
        totalDurationInFrames: 300,
      } as AdProps}
      calculateMetadata={({ props }) => ({
        durationInFrames: props.totalDurationInFrames,
        fps: props.fps,
        width: props.width,
        height: props.height,
      })}
    />
    </>
  );
};
