/**
 * Punch.tsx — vlastné prechody na čistom CSS.
 *
 * Prečo vlastné:
 *  - HTML-in-canvas prechody (dreamyZoom, linearBlur, filmBurn…) spôsobujú,
 *    že hotové video pri prehrávaní laguje. Overené A/B testom 2026-09-19.
 *  - Hotové CSS prechody (slide, wipe, flip, clockWipe, iris) vyzerajú
 *    ako prezentácia v PowerPointe. Nepoužívajú sa..
 *
 * Tieto používajú len `transform` a `opacity`, takže sú rovnako bezpečné
 * ako fade, ale pôsobia ako strih vo videu, nie ako posúvanie slidov.
 */
import React from "react";
import { AbsoluteFill, interpolate, Easing } from "remotion";
import type {
  TransitionPresentation,
  TransitionPresentationComponentProps,
} from "@remotion/transitions";

type PunchProps = { strength?: number };

/** Jemný zoom cez seba — odchádzajúci záber sa pritiahne, prichádzajúci dosadne. */
const PunchComp: React.FC<TransitionPresentationComponentProps<PunchProps>> = ({
  children,
  presentationProgress: p,
  presentationDirection,
  passedProps,
}) => {
  const s = passedProps.strength ?? 0.07;
  const entering = presentationDirection === "entering";
  const eased = interpolate(p, [0, 1], [0, 1], {
    easing: Easing.bezier(0.4, 0, 0.2, 1),
  });

  const scale = entering
    ? interpolate(eased, [0, 1], [1 + s, 1])
    : interpolate(eased, [0, 1], [1, 1 - s * 0.6]);
  const opacity = entering ? eased : 1 - eased;

  return (
    <AbsoluteFill style={{ opacity, transform: `scale(${scale})` }}>
      {children}
    </AbsoluteFill>
  );
};

export const punch = (props: PunchProps = {}): TransitionPresentation<PunchProps> => ({
  component: PunchComp,
  props,
});

/** Rýchle presvetlenie — ako keby cez strih prebehol záblesk. Bez posúvania. */
const FlashComp: React.FC<TransitionPresentationComponentProps<PunchProps>> = ({
  children,
  presentationProgress: p,
  presentationDirection,
}) => {
  const entering = presentationDirection === "entering";
  const opacity = entering ? interpolate(p, [0.35, 1], [0, 1], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp",
  }) : interpolate(p, [0, 0.65], [1, 0], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp",
  });
  // biely nádych uprostred strihu
  const flash = interpolate(p, [0, 0.5, 1], [0, 0.55, 0], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ opacity }}>
      {children}
      {entering ? (
        <AbsoluteFill style={{ background: "#fff", opacity: flash }} />
      ) : null}
    </AbsoluteFill>
  );
};

export const flash = (props: PunchProps = {}): TransitionPresentation<PunchProps> => ({
  component: FlashComp,
  props,
});
