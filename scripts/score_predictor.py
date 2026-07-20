#!/home/hiesl/phd/plot/.venv/bin/python3

"""
World Cup Score Predictor from Betting Odds
============================================
Given decimal betting odds (home / draw / away), derives the most likely
scoreline AND the scoreline that maximizes expected Kicktipp points.

Kicktipp "Turnier" scoring (neutral ground, so home/away symmetric):
  Guess is a WIN:
    4 pts — exact score correct
    3 pts — goal difference correct (but not exact score)
    2 pts — correct winner, wrong goal difference
    0 pts — wrong outcome
  Guess is a DRAW:
    4 pts — exact score correct  (e.g. guessed 1-1, result 1-1)
    3 pts — any other correct draw (e.g. guessed 1-1, result 0-0)
    0 pts — result was a win

Fitting:
  Both lambda_home and lambda_away are fitted simultaneously to match
  the implied P(home win) and P(draw) from the odds — no avg_goals
  assumption needed. Dixon-Coles correction (rho=-0.13) is applied to
  fix Poisson's known draw underestimation.

Knockout mode (--knockout):
  Use after-90-min 1X2 odds as usual. Draw scorelines are simply
  excluded from the optimizer — the home/away asymmetry in the fitted
  lambdas naturally breaks any tie between e.g. 1-0 and 0-1.

Usage:
  python score_predictor.py --home 1.40 --draw 4.60 --away 8.25
  python score_predictor.py --home 2.60 --draw 3.00 --away 2.90 -v
  python score_predictor.py --knockout --home 1.55 --draw 4.20 --away 2.60 -v
"""

import argparse
from math import exp, factorial
from scipy.optimize import root, brentq
from scipy.stats import skellam

def poisson_pmf(k: int, lam: float) -> float:
    return (lam**k * exp(-lam)) / factorial(k)

def dixon_coles_correction(h: int, a: int, lam_h: float, lam_a: float, rho: float = -0.13) -> float:
    """Correction for low-scoring results to fix Poisson's draw underestimation."""
    if h == 0 and a == 0: return 1 - lam_h * lam_a * rho
    if h == 1 and a == 0: return 1 + lam_a * rho
    if h == 0 and a == 1: return 1 + lam_h * rho
    if h == 1 and a == 1: return 1 - rho
    return 1.0

def score_matrix(lam_h: float, lam_a: float, max_goals: int = 8) -> list[list[float]]:
    mat = [
        [poisson_pmf(h, lam_h) * poisson_pmf(a, lam_a)
         * dixon_coles_correction(h, a, lam_h, lam_a)
         for a in range(max_goals + 1)]
        for h in range(max_goals + 1)
    ]
    total = sum(mat[h][a] for h in range(max_goals+1) for a in range(max_goals+1))
    return [[mat[h][a] / total for a in range(max_goals+1)] for h in range(max_goals+1)]

def extra_time_matrix(
    mat: list[list[float]],
    lam_h: float,
    lam_a: float,
    et_scale: float = 0.5,
    et_minutes: int = 30,
    regulation_minutes: int = 90,
    max_et_goals: int = 2,
) -> list[list[float]]:
    """
    Redistribute 90'-draw probability mass into the after-extra-time (120')
    score distribution.

    Extra time is only played when the score is level after 90 minutes, so
    non-draw cells in `mat` are already final results and are left
    untouched. Each draw cell (h, h) is convolved with a low-scoring
    Poisson process representing the extra 30 minutes (rates scaled down
    from the 90' rates by et_scale), splitting its probability mass across
    (h, h), (h+1, h), (h, h+1), (h+1, h+1), etc.
    """
    n = len(mat)
    lam_h_et = lam_h * (et_minutes / regulation_minutes) * et_scale
    lam_a_et = lam_a * (et_minutes / regulation_minutes) * et_scale

    w_h = [poisson_pmf(k, lam_h_et) for k in range(max_et_goals + 1)]
    w_h[-1] = 1 - sum(w_h[:-1])  # lump remaining tail mass into the cap
    w_a = [poisson_pmf(k, lam_a_et) for k in range(max_et_goals + 1)]
    w_a[-1] = 1 - sum(w_a[:-1])

    final = [row[:] for row in mat]
    for h in range(n):
        p_draw = mat[h][h]
        if p_draw == 0:
            continue
        final[h][h] = 0.0
        for dh in range(max_et_goals + 1):
            for da in range(max_et_goals + 1):
                fh, fa = min(h + dh, n - 1), min(h + da, n - 1)
                final[fh][fa] += p_draw * w_h[dh] * w_a[da]

    total = sum(final[h][a] for h in range(n) for a in range(n))
    return [[final[h][a] / total for a in range(n)] for h in range(n)]

def fit_et_scale(
    lam_h: float,
    lam_a: float,
    p_home_90: float,
    p_draw_90: float,
    target_p_home_adv: float,
    pen_home_prob: float = 0.5,
    et_minutes: int = 30,
    regulation_minutes: int = 90,
    max_et_scale: float = 1.5,
) -> tuple[float, float]:
    """
    Back out the extra-time scoring-rate scale factor implied by the
    "to advance" market — but only within a physically plausible range
    (et_scale capped at max_et_scale, i.e. extra time scoring at most as
    fast as regulation time; realistically it usually runs slower).

    P(home advances) = P(home wins in 90')
                      + P(draw in 90') * [ P(home wins in ET)
                                          + P(level after ET) * P(home wins penalties) ]

    Note this only calibrates et_scale, not pen_home_prob (fixed at 0.5):
    a shootout-skill edge would show up in the advance odds too, but it
    can NEVER be reflected in the score matrix, because a penalty
    shootout does not change the recorded scoreline (still e.g. 1-1 AET)
    — Kicktipp grades the AET score, not who won on penalties. So any
    part of the market's skew that can't be explained by a plausible
    et_scale is left unmodeled here and reported as a diagnostic instead
    of silently forced into a parameter with no effect on the prediction.

    Returns (et_scale, residual_gap) where residual_gap is how far short
    the capped fit falls of matching the market's advance probability
    (0 if the fit landed inside the bracket cleanly).
    """
    def implied_p_home_adv(s: float) -> float:
        lam_h_et = lam_h * (et_minutes / regulation_minutes) * s
        lam_a_et = lam_a * (et_minutes / regulation_minutes) * s
        p_home_win_et = 1 - skellam.cdf(0, lam_h_et, lam_a_et)
        p_level_et = skellam.pmf(0, lam_h_et, lam_a_et)
        return p_home_90 + p_draw_90 * (p_home_win_et + p_level_et * pen_home_prob)

    def equation(s: float) -> float:
        return implied_p_home_adv(s) - target_p_home_adv

    lo, hi = 1e-4, max_et_scale
    if equation(lo) * equation(hi) > 0:
        s = lo if abs(equation(lo)) < abs(equation(hi)) else hi
        residual_gap = target_p_home_adv - implied_p_home_adv(s)
        return s, residual_gap

    return brentq(equation, lo, hi), 0.0

def outcome_probs(matrix: list[list[float]]) -> tuple[float, float, float]:
    n = len(matrix)
    p_home = sum(matrix[h][a] for h in range(n) for a in range(n) if h > a)
    p_draw = sum(matrix[h][a] for h in range(n) for a in range(n) if h == a)
    p_away = sum(matrix[h][a] for h in range(n) for a in range(n) if h < a)
    return p_home, p_draw, p_away

def normalize_odds(home_odds: float, draw_odds: float, away_odds: float) -> tuple[float, float, float]:
    raw = [1/home_odds, 1/draw_odds, 1/away_odds]
    total = sum(raw)
    return raw[0]/total, raw[1]/total, raw[2]/total

def fit_lambdas(p_home_target: float, p_draw_target: float, max_goals: int = 8) -> tuple[float, float]:
    """
    Fit lam_h and lam_a simultaneously so that the score matrix reproduces
    both P(home win) and P(draw) from the normalized odds.
    No avg_goals assumption needed — the draw probability already encodes
    information about expected goal volume.
    """
    def equations(x):
        lam_h, lam_a = x
        if lam_h <= 0 or lam_a <= 0:
            return [1e6, 1e6]
        mat = score_matrix(lam_h, lam_a, max_goals)
        p_home, p_draw, _ = outcome_probs(mat)
        return [p_home - p_home_target, p_draw - p_draw_target]

    # Initial guess: start from equal lambdas around 1.3
    sol = root(equations, [1.4, 1.2])
    if not sol.success:
        raise RuntimeError(f"Could not fit lambdas: {sol.message}")
    return float(sol.x[0]), float(sol.x[1])

def kicktipp_points(guess_h: int, guess_a: int, actual_h: int, actual_a: int) -> int:
    guess_is_draw  = (guess_h  == guess_a)
    actual_is_draw = (actual_h == actual_a)

    if guess_h == actual_h and guess_a == actual_a:
        return 4
    if guess_is_draw:
        return 3 if actual_is_draw else 0
    else:
        if actual_is_draw:
            return 0
        if (guess_h - guess_a) == (actual_h - actual_a):
            return 3
        guess_winner  = 1 if guess_h  > guess_a  else -1
        actual_winner = 1 if actual_h > actual_a else -1
        return 2 if guess_winner == actual_winner else 0

def expected_points(guess_h: int, guess_a: int, mat: list[list[float]]) -> float:
    total = 0.0
    for ah in range(len(mat)):
        for aa in range(len(mat[0])):
            total += kicktipp_points(guess_h, guess_a, ah, aa) * mat[ah][aa]
    return total

def analyse(
    home_odds: float,
    draw_odds: float,
    away_odds: float,
    knockout: bool = False,
    home_adv_odds: float | None = None,
    away_adv_odds: float | None = None,
    et_scale: float = 0.5,
    top_n: int = 10,
    verbose: bool = False,
    ) -> None:

    MAX_GOALS = 8

    p_home, p_draw, p_away = normalize_odds(home_odds, draw_odds, away_odds)
    overround = (1/home_odds + 1/draw_odds + 1/away_odds - 1) * 100

    lam_h, lam_a = fit_lambdas(p_home, p_draw, MAX_GOALS)
    mat = score_matrix(lam_h, lam_a, MAX_GOALS)
    ph, pd, pa = outcome_probs(mat)

    # Kicktipp grades knockout matches against the score after extra time,
    # not the 90-minute score. ET is only played on a 90' draw, so shift
    # that mass into the final (AET) distribution before optimizing guesses.
    et_scale_fitted = None
    residual_gap = None
    p_home_adv_target = None
    if knockout:
        if home_adv_odds is not None and away_adv_odds is not None:
            raw_adv = [1/home_adv_odds, 1/away_adv_odds]
            p_home_adv_target = raw_adv[0] / sum(raw_adv)
            et_scale, residual_gap = fit_et_scale(lam_h, lam_a, ph, pd, p_home_adv_target)
            et_scale_fitted = et_scale
        final_mat = extra_time_matrix(mat, lam_h, lam_a, et_scale)
    else:
        final_mat = mat

    # In knockout mode only consider non-draw scorelines as guesses
    # (Kicktipp forces a decisive guess for KO ties in this cup's ruleset).
    all_scores = [
        (final_mat[h][a], expected_points(h, a, final_mat), h, a)
        for h in range(MAX_GOALS + 1)
        for a in range(MAX_GOALS + 1)
        if not (knockout and h == a)
    ]
    by_prob = sorted(all_scores, key=lambda x: -x[0])
    by_pts  = sorted(all_scores, key=lambda x: -x[1])
    best_prob_score = by_prob[0]
    best_pts_score  = by_pts[0]

    if verbose:
        print("=" * 57)
        mode_label = "KNOCKOUT" if knockout else "GROUP STAGE"
        print(f"  WORLD CUP SCORE PREDICTOR  —  {mode_label}")
        print("=" * 57)
        print(f"\nOdds:  Home {home_odds}  ·  Draw {draw_odds}  ·  Away {away_odds}")
        print(f"Bookmaker overround: {overround:.1f}%")
        print(f"\nNormalized probabilities:")
        print(f"  Home win : {p_home*100:5.1f}%")
        print(f"  Draw     : {p_draw*100:5.1f}%")
        print(f"  Away win : {p_away*100:5.1f}%")

        print(f"\nFitted Poisson rates:")
        print(f"  λ home = {lam_h:.3f}  ·  λ away = {lam_a:.3f}")
        print(f"  Implied avg goals/game: {lam_h + lam_a:.2f}")

        print(f"\nVerification (model vs. target):")
        print(f"  Home win : {ph*100:5.1f}%  (target {p_home*100:.1f}%)")
        print(f"  Draw     : {pd*100:5.1f}%  (target {p_draw*100:.1f}%)")
        print(f"  Away win : {pa*100:5.1f}%  (target {p_away*100:.1f}%)")

        if knockout:
            residual_draw = sum(final_mat[h][h] for h in range(MAX_GOALS + 1))
            print(f"\nExtra-time model:")
            if et_scale_fitted is not None:
                print(f"  Advance odds:  Home {home_adv_odds}  ·  Away {away_adv_odds}")
                print(f"  Target P(home advances): {p_home_adv_target*100:.1f}%")
                print(f"  Calibrated et_scale: {et_scale_fitted:.3f}  (fitted from advance odds,")
                print(f"    assuming 50/50 penalties)")
                if residual_gap is not None and abs(residual_gap) > 0.005:
                    print(f"  Note: fit hit the plausible-range boundary; "
                          f"{abs(residual_gap)*100:.1f}pp of the advance-odds")
                    print(f"    skew is unexplained by ET goalscoring alone — likely reflects")
                    print(f"    penalty-shootout factors, which don't affect the graded")
                    print(f"    scoreline and so aren't modeled here.")
            else:
                print(f"  et_scale: {et_scale} (manual default — pass --home-adv/--away-adv")
                print(f"    to calibrate from the advance-to-next-round market instead)")
            print(f"  Residual AET draw probability: {residual_draw*100:.2f}%")
            print(f"  Note: probabilities below are AFTER extra time; draw scorelines")
            print(f"  are excluded from guesses.")

        header  = f"  {'Score':<9} {'Prob':>7}  {'E[pts]':>7}  Outcome"
        divider = f"  {'-'*43}"

        print(f"\nTop {top_n} by raw probability:")
        print(header); print(divider)
        for prob, epts, h, a in by_prob[:top_n]:
            outcome = "Home win" if h > a else ("Draw" if h == a else "Away win")
            print(f"  {h} – {a:<6}  {prob*100:>6.2f}%  {epts:>7.3f}  {outcome}")

        print(f"\nTop {top_n} by expected Kicktipp points:")
        print(header); print(divider)
        for prob, epts, h, a in by_pts[:top_n]:
            outcome = "Home win" if h > a else ("Draw" if h == a else "Away win")
            print(f"  {h} – {a:<6}  {prob*100:>6.2f}%  {epts:>7.3f}  {outcome}")

        print(f"\n{'=' * 57}")
        print(f"  Most likely score :  {best_prob_score[2]} – {best_prob_score[3]}"
              f"  (prob {best_prob_score[0]*100:.1f}%,  E[pts] {best_prob_score[1]:.3f})")
        print(f"  Best Kicktipp guess: {best_pts_score[2]} – {best_pts_score[3]}"
              f"  (prob {best_pts_score[0]*100:.1f}%,  E[pts] {best_pts_score[1]:.3f})")
        if (best_prob_score[2], best_prob_score[3]) != (best_pts_score[2], best_pts_score[3]):
            gain = best_pts_score[1] - best_prob_score[1]
            print(f"  → Optimizing for points gains +{gain:.3f} E[pts] over most-likely guess")
        else:
            print(f"  → Both methods agree on the same scoreline ✓")
        print("=" * 57)
    else:
        print(f"Most likely score:   {best_prob_score[2]} – {best_prob_score[3]}")
        print(f"Best Kicktipp guess: {best_pts_score[2]} – {best_pts_score[3]}")

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Predict WC scorelines from decimal betting odds, optimized for Kicktipp.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Group stage:    %(prog)s --home 1.40 --draw 4.60 --away 8.25\n"
            "Knockout round: %(prog)s --knockout --home 1.55 --draw 4.20 --away 2.60"
        ),
    )

    parser.add_argument("--knockout", action="store_true",
        help="knockout mode: use after-90-min 1X2 odds; draw scorelines excluded from guesses")

    parser.add_argument("--home", type=float, required=True,
        help="home win odds")

    parser.add_argument("--draw", type=float, required=True,
        help="draw odds (after 90 min for knockout)")

    parser.add_argument("--away", type=float, required=True,
        help="away win odds")

    parser.add_argument("--home-adv", type=float,
        help="knockout only: odds for home team to advance to next round "
             "(2-way market, after ET/penalties). Required with --knockout "
             "unless --et-scale is given manually")

    parser.add_argument("--away-adv", type=float,
        help="knockout only: odds for away team to advance to next round")

    parser.add_argument("--et-scale", type=float, default=None,
        help="knockout only: manually set the extra-time scoring rate as a "
             "fraction of the 90-minute rate, instead of calibrating it "
             "from --home-adv/--away-adv (default if neither given: 0.5)")

    parser.add_argument("--top", type=int, default=10,
        help="number of top scorelines to show (default: 10)")

    parser.add_argument("-v", "--verbose", action="store_true",
        help="print verbose output")

    args = parser.parse_args()

    if args.knockout:
        have_adv_odds = args.home_adv is not None and args.away_adv is not None
        if not have_adv_odds and args.et_scale is None:
            parser.error(
                "--knockout requires either both --home-adv and --away-adv "
                "(to calibrate extra-time scoring from the market), or an "
                "explicit --et-scale to skip calibration."
            )
        if (args.home_adv is None) != (args.away_adv is None):
            parser.error("--home-adv and --away-adv must be given together.")

    analyse(
        home_odds=args.home,
        draw_odds=args.draw,
        away_odds=args.away,
        knockout=args.knockout,
        home_adv_odds=args.home_adv,
        away_adv_odds=args.away_adv,
        et_scale=args.et_scale if args.et_scale is not None else 0.5,
        top_n=args.top,
        verbose=args.verbose,
    )

if __name__ == "__main__":
    main()
