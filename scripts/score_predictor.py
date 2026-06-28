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
from scipy.optimize import root

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
    top_n: int = 10,
    verbose: bool = False,
    ) -> None:

    MAX_GOALS = 8

    p_home, p_draw, p_away = normalize_odds(home_odds, draw_odds, away_odds)
    overround = (1/home_odds + 1/draw_odds + 1/away_odds - 1) * 100

    lam_h, lam_a = fit_lambdas(p_home, p_draw, MAX_GOALS)
    mat = score_matrix(lam_h, lam_a, MAX_GOALS)
    ph, pd, pa = outcome_probs(mat)

    # In knockout mode only consider non-draw scorelines as guesses.
    all_scores = [
        (mat[h][a], expected_points(h, a, mat), h, a)
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
            print(f"\n  Note: draw scorelines excluded from guesses.")

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

    parser.add_argument("--top", type=int, default=10,
        help="number of top scorelines to show (default: 10)")

    parser.add_argument("-v", "--verbose", action="store_true",
        help="print verbose output")

    args = parser.parse_args()

    analyse(
        home_odds=args.home,
        draw_odds=args.draw,
        away_odds=args.away,
        knockout=args.knockout,
        top_n=args.top,
        verbose=args.verbose,
    )

if __name__ == "__main__":
    main()
