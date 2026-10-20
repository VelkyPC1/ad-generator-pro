import {
  AbsoluteFill,
  Img,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
  spring,
  interpolate,
  Easing,
} from "remotion";
import { loadFont } from "@remotion/google-fonts/Montserrat";

const { fontFamily } = loadFont("normal", { weights: ["600", "700", "800", "900"] });

const MAGENTA = "#4F52F7"; // akcent (predvolená farba AdGenerator)
const PLUM = "#13161D";    // tmavé pozadie kariet

export type FlashPhotoProps = {
  image: string;
  fps: number;
  width: number;
  height: number;
  durationSec: number;

  headline: string;   // "PRODUKT + DARČEK"
  freeWord: string;   // "ZADARMO"
  bullets: string[];
  priceFrom: number;
  priceTo: number;
  currency: string;
  discount: string;   // "-58 %"
  cta: string;
};

// ── časová os (s) ──────────────────────────────────────────────────────
const T = {
  headline: 0.5,
  free: 0.9,
  bullets: 2.3,   // + 0.3 s stagger
  price: 4.3,
  strike: 5.1,
  badge: 5.4,
  cta: 6.3,
};

/**
 * Rozloženie je odvodené od toho, kde na fotke reálne je tvár a produkt:
 *   tvár  ≈ y 430–760
 *   produkt ≈ y 570–1180
 * Text preto ide LEN nad hlavu (240–420) a pod produkt (1210–1660).
 * Stredné pásmo zostáva úplne voľné — produkt ani tvár nič neprekrýva.
 *
 * Safe zone (Meta Reels/Stories): horných ~230 px a spodných ~260 px berie UI platformy.
 */
const TOP_BAND = 240;      // horná hrana textu — nad hlavou, pod safe zone
const BOTTOM_BAND = 262;   // spodná hrana textu — nad UI platformy

const money = (n: number, cur: string) => {
  const s = n.toFixed(2).replace(".", ",");
  return cur === "€" ? `${s} €` : `${s} ${cur}`;
};

const popIn = (t: number, start: number, fps: number, frame: number, dy = 34) => {
  if (t < start) return { opacity: 0, transform: `translateY(${dy}px) scale(0.94)` };
  const s = spring({
    frame: frame - start * fps,
    fps,
    config: { damping: 15, stiffness: 130, mass: 0.7 },
  });
  return {
    opacity: interpolate(s, [0, 1], [0, 1]),
    transform: `translateY(${interpolate(s, [0, 1], [dy, 0])}px) scale(${interpolate(
      s,
      [0, 1],
      [0.94, 1]
    )})`,
  };
};

export const FlashPhoto: React.FC<FlashPhotoProps> = (p) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const t = frame / fps;

  // Fotka bez posunu — kompozíciu držíme presne tam, kde bola zameraná.
  // Ken Burns je jemný, aby sa tvár ani produkt nedostali pod text.
  const zoom = interpolate(frame, [0, durationInFrames], [1.0, 1.04], {
    extrapolateRight: "clamp",
  });

  const priceProgress = interpolate(t, [T.price + 0.25, T.price + 1.4], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  const priceNow = p.priceFrom + (p.priceTo - p.priceFrom) * priceProgress;

  const strike = interpolate(t, [T.strike, T.strike + 0.45], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.quad),
  });

  const ctaPulse = t >= T.cta ? 1 + 0.03 * Math.sin((t - T.cta) * 5.2) : 1;

  return (
    <AbsoluteFill style={{ fontFamily, backgroundColor: PLUM }}>
      <AbsoluteFill>
        <Img
          src={staticFile(p.image)}
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover",
            transform: `scale(${zoom})`,
          }}
        />
      </AbsoluteFill>

      {/* Čitateľnosť: tmavne LEN horný a dolný pás, kde text je.
          Stredné pásmo (tvár + produkt) zostáva úplne čisté. */}
      <AbsoluteFill
        style={{
          background:
            "linear-gradient(180deg, rgba(23,12,33,0.78) 0%, rgba(23,12,33,0.50) 16%, rgba(23,12,33,0.00) 26%, rgba(23,12,33,0.00) 58%, rgba(23,12,33,0.55) 70%, rgba(23,12,33,0.90) 88%, rgba(23,12,33,0.94) 100%)",
        }}
      />

      {/* ══ HORNÝ PÁS — nad hlavou (končí ~y 420, tvár začína ~430) ══ */}
      <div
        style={{
          position: "absolute",
          top: TOP_BAND,
          left: 0,
          right: 0,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          textAlign: "center",
        }}
      >
        <div
          style={{
            fontWeight: 800,
            fontSize: 38,
            letterSpacing: 2,
            color: "#fff",
            textShadow: "0 3px 18px rgba(0,0,0,0.7)",
            ...popIn(t, T.headline, fps, frame, 22),
          }}
        >
          {p.headline}
        </div>

        {/* ZADARMO — čistá typografia: plná biela, jeden mäkký tieň. Žiadny obrys ani
            posunutý duplikát — tie predtým robili zubatý „zig-zag" okraj. */}
        <div
          style={{
            marginTop: 2,
            fontWeight: 900,
            fontSize: 116,
            lineHeight: 1.05,
            color: "#fff",
            letterSpacing: -1,
            textShadow: "0 8px 30px rgba(0,0,0,0.6)",
            ...popIn(t, T.free, fps, frame, 26),
          }}
        >
          {p.freeWord}
        </div>
      </div>

      {/* ══ DOLNÝ PÁS — pod produktom (začína ~y 1210, produkt končí ~1180) ══ */}
      <div
        style={{
          position: "absolute",
          bottom: BOTTOM_BAND,
          left: 0,
          right: 0,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: 20,
        }}
      >
        {/* odrážky */}
        <div style={{ display: "flex", flexDirection: "column", gap: 12, alignItems: "flex-start" }}>
          {p.bullets.map((b, i) => {
            const start = T.bullets + i * 0.3;
            const s =
              t < start
                ? 0
                : spring({
                    frame: frame - start * fps,
                    fps,
                    config: { damping: 15, stiffness: 120 },
                  });
            return (
              <div
                key={i}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 14,
                  opacity: s,
                  transform: `translateY(${interpolate(s, [0, 1], [18, 0])}px)`,
                }}
              >
                <div
                  style={{
                    width: 38,
                    height: 38,
                    borderRadius: "50%",
                    background: MAGENTA,
                    color: "#fff",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontSize: 22,
                    fontWeight: 900,
                    flexShrink: 0,
                  }}
                >
                  ✓
                </div>
                <div
                  style={{
                    fontSize: 36,
                    fontWeight: 700,
                    color: "#fff",
                    textShadow: "0 3px 14px rgba(0,0,0,0.75)",
                  }}
                >
                  {b}
                </div>
              </div>
            );
          })}
        </div>

        {/* ceny — v osi, stará vľavo, nová v pilulke vpravo */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: 22,
            ...popIn(t, T.price, fps, frame, 22),
          }}
        >
          <div style={{ position: "relative", display: "inline-block" }}>
            <div
              style={{
                fontSize: 48,
                fontWeight: 700,
                color: "rgba(255,255,255,0.8)",
                textShadow: "0 3px 14px rgba(0,0,0,0.7)",
              }}
            >
              {money(p.priceFrom, p.currency)}
            </div>
            <div
              style={{
                position: "absolute",
                left: -6,
                right: -6,
                top: "52%",
                height: 6,
                background: MAGENTA,
                borderRadius: 3,
                transform: `scaleX(${strike}) rotate(-7deg)`,
                transformOrigin: "left center",
              }}
            />
          </div>

          <div
            style={{
              background: "#fff",
              color: PLUM,
              borderRadius: 999,
              padding: "12px 34px",
              fontSize: 66,
              fontWeight: 900,
              letterSpacing: -2,
              boxShadow: "0 14px 40px rgba(0,0,0,0.45)",
              fontVariantNumeric: "tabular-nums",
            }}
          >
            {money(priceNow, p.currency)}
          </div>

          {/* zľava — dorazí až po dopočítaní ceny, v tej istej osi ako ceny.
              Hore by padla priamo na tvár, preto je tu. */}
          <div
            style={{
              background: MAGENTA,
              color: "#fff",
              borderRadius: 999,
              padding: "12px 26px",
              fontSize: 44,
              fontWeight: 900,
              boxShadow: "0 12px 32px rgba(226,9,126,0.5)",
              ...popIn(t, T.badge, fps, frame, 14),
            }}
          >
            {p.discount}
          </div>
        </div>

        {/* CTA */}
        <div style={{ ...popIn(t, T.cta, fps, frame, 20) }}>
          <div
            style={{
              background: MAGENTA,
              color: "#fff",
              borderRadius: 999,
              padding: "24px 84px",
              fontSize: 48,
              fontWeight: 900,
              letterSpacing: 1,
              boxShadow: "0 16px 44px rgba(226,9,126,0.55)",
              transform: `scale(${ctaPulse})`,
            }}
          >
            {p.cta}
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};
