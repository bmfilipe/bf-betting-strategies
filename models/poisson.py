import numpy as np
import math

class PoissonEngine:
    """
    Quantitative statistical engine based on Poisson distributions
    and expected goals (xG / xGA) metrics.
    """

    @staticmethod
    def calculate_implied_prob(odd: float) -> float:
        """Calculate market implied probability percentage from decimal odds."""
        if odd <= 1.0:
            return 0.0
        return (1.0 / odd) * 100.0

    @staticmethod
    def calculate_ev(prob_estimated_pct: float, odd: float) -> float:
        """Calculate Expected Value (+EV) percentage."""
        prob_decimal = prob_estimated_pct / 100.0
        ev = ((prob_decimal * odd) - 1.0) * 100.0
        return round(ev, 2)

    @staticmethod
    def calculate_kelly_stake(prob_estimated_pct: float, odd: float, bankroll: float = 1000.0, fraction: float = 0.25) -> tuple[float, float]:
        """
        Calculate Fractional Kelly Criterion Stake.
        Returns (kelly_pct, recommended_stake_eur).
        """
        if odd <= 1.0 or bankroll <= 0:
            return 0.0, 0.0
        b = odd - 1.0
        p = prob_estimated_pct / 100.0
        q = 1.0 - p
        full_kelly = (p * b - q) / b if b > 0 else 0.0
        frac_kelly = max(0.0, full_kelly) * fraction
        stake_eur = bankroll * frac_kelly
        return round(frac_kelly * 100.0, 2), round(stake_eur, 2)

    @staticmethod
    def poisson_pmf(lmbda: float, k: int) -> float:
        """Calculate Poisson Probability Mass Function for lambda and count k."""
        if lmbda <= 0:
            return 1.0 if k == 0 else 0.0
        return (math.pow(lmbda, k) * math.exp(-lmbda)) / math.factorial(k)

    @staticmethod
    def calculate_match_probabilities(exp_g_home: float, exp_g_away: float) -> dict:
        """
        Calculate 1X2, Over 2.5 and BTTS probabilities and fair odds
        directly from expected home and away goals using Poisson distribution.
        """
        engine = PoissonEngine()
        prob_matrix = engine.generate_probability_matrix(exp_g_home, exp_g_away, matrix_size=7)

        p_home = float(np.sum(np.tril(prob_matrix, -1)))
        p_draw = float(np.sum(np.diag(prob_matrix)))
        p_away = float(np.sum(np.triu(prob_matrix, 1)))

        p_o25 = float(np.sum([prob_matrix[h][a] for h in range(7) for a in range(7) if (h + a) > 2.5]))
        p_btts_yes = float(np.sum([prob_matrix[h][a] for h in range(1, 7) for a in range(1, 7)]))

        def fair_odd(p: float) -> float:
            return round(1.0 / p, 2) if p > 0.001 else 99.00

        return {
            "prob_home_win": p_home,
            "fair_odd_1": fair_odd(p_home),
            "prob_draw": p_draw,
            "fair_odd_x": fair_odd(p_draw),
            "prob_away_win": p_away,
            "fair_odd_2": fair_odd(p_away),
            "prob_over_25": p_o25,
            "fair_odd_o25": fair_odd(p_o25),
            "prob_btts_yes": p_btts_yes,
            "fair_odd_btts_yes": fair_odd(p_btts_yes)
        }

    def dixon_coles_tau(self, h: int, a: int, lmbda: float, mu: float, rho: float = -0.13) -> float:
        """
        Dixon-Coles adjustment factor for low-scoring outcomes (0-0, 1-0, 0-1, 1-1).
        Corrects standard Poisson independence assumption for low scores.
        """
        if h == 0 and a == 0:
            return max(0.0, 1.0 - (lmbda * mu * rho))
        elif h == 1 and a == 0:
            return max(0.0, 1.0 + (mu * rho))
        elif h == 0 and a == 1:
            return max(0.0, 1.0 + (lmbda * rho))
        elif h == 1 and a == 1:
            return max(0.0, 1.0 - rho)
        return 1.0

    def generate_probability_matrix(self, exp_g_home: float, exp_g_away: float, matrix_size: int = 7, rho: float = -0.13) -> np.ndarray:
        """Generate a 7x7 joint scoreline probability matrix with Dixon-Coles bivariate correction."""
        matrix = np.zeros((matrix_size, matrix_size))
        for h in range(matrix_size):
            for a in range(matrix_size):
                base_p = self.poisson_pmf(exp_g_home, h) * self.poisson_pmf(exp_g_away, a)
                tau = self.dixon_coles_tau(h, a, exp_g_home, exp_g_away, rho=rho)
                matrix[h][a] = base_p * tau

        # Re-normalize matrix so probabilities sum to 1.0
        total_p = np.sum(matrix)
        if total_p > 0:
            matrix = matrix / total_p
        return matrix

    def analyze_match(
        self,
        home: str,
        away: str,
        h_xg: float,
        a_xg: float,
        h_xga: float,
        a_xga: float,
        odd: float,
        market: str,
        country: str = "Geral",
        league: str = "Geral"
    ) -> dict:
        """
        Analyze a match using Dixon-Coles Poisson matrix and return expected goals,
        probabilities for all markets, EV, and matrix details.
        """
        # Adjusted Expected Goals
        exp_g_home = (h_xg + a_xga) / 2.0
        exp_g_away = (a_xg + h_xga) / 2.0

        prob_matrix = self.generate_probability_matrix(exp_g_home, exp_g_away, matrix_size=7, rho=-0.13)

        # 1X2 Probabilities
        p_home = float(np.sum(np.tril(prob_matrix, -1)))
        p_draw = float(np.sum(np.diag(prob_matrix)))
        p_away = float(np.sum(np.triu(prob_matrix, 1)))

        # Goal Totals
        p_o05 = float(np.sum([prob_matrix[h][a] for h in range(7) for a in range(7) if (h + a) > 0.5]))
        p_o15 = float(np.sum([prob_matrix[h][a] for h in range(7) for a in range(7) if (h + a) > 1.5]))
        p_o25 = float(np.sum([prob_matrix[h][a] for h in range(7) for a in range(7) if (h + a) > 2.5]))
        p_o35 = float(np.sum([prob_matrix[h][a] for h in range(7) for a in range(7) if (h + a) > 3.5]))
        p_u25 = 1.0 - p_o25

        # Both Teams To Score (BTTS)
        p_btts_yes = float(np.sum([prob_matrix[h][a] for h in range(1, 7) for a in range(1, 7)]))
        p_btts_no = 1.0 - p_btts_yes

        # Double Chance
        p_1x = p_home + p_draw
        p_x2 = p_away + p_draw
        p_12 = p_home + p_away

        # Draw No Bet (DNB)
        p_dnb1 = p_home / (p_home + p_away) if (p_home + p_away) > 0 else 0.5
        p_dnb2 = p_away / (p_home + p_away) if (p_home + p_away) > 0 else 0.5

        # Asian Handicap (AH)
        p_ah_h_minus05 = p_home
        p_ah_a_plus05 = p_x2
        p_ah_h_plus05 = p_1x
        p_ah_a_minus05 = p_away

        # AH 1.0 margin
        p_h_win_2plus = float(np.sum([prob_matrix[h][a] for h in range(7) for a in range(7) if (h - a) >= 2]))
        p_h_win_1 = float(np.sum([prob_matrix[h][a] for h in range(7) for a in range(7) if (h - a) == 1]))
        p_ah_h_minus10 = p_h_win_2plus + (0.5 * p_h_win_1)
        p_ah_a_plus10 = p_x2 + (0.5 * p_h_win_1)

        market_prob_map = {
            "Vitória Casa (1)": p_home * 100.0,
            "Empate (X)": p_draw * 100.0,
            "Vitória Fora (2)": p_away * 100.0,
            "Dupla Hipótese (1X)": p_1x * 100.0,
            "Dupla Hipótese (X2)": p_x2 * 100.0,
            "Dupla Hipótese (12)": p_12 * 100.0,
            "Total +0.5 Golos": p_o05 * 100.0,
            "Total +1.5 Golos": p_o15 * 100.0,
            "Total +2.5 Golos": p_o25 * 100.0,
            "Total +3.5 Golos": p_o35 * 100.0,
            "Total -2.5 Golos": p_u25 * 100.0,
            "Ambas Marcam (Sim)": p_btts_yes * 100.0,
            "Ambas Marcam (Não)": p_btts_no * 100.0,
            "Empate Anula Casa (DNB 1)": p_dnb1 * 100.0,
            "Empate Anula Fora (DNB 2)": p_dnb2 * 100.0,
            "Handicap Asiático Casa (AH -0.5)": p_ah_h_minus05 * 100.0,
            "Handicap Asiático Fora (AH +0.5)": p_ah_a_plus05 * 100.0,
            "Handicap Asiático Casa (AH +0.5)": p_ah_h_plus05 * 100.0,
            "Handicap Asiático Fora (AH -0.5)": p_ah_a_minus05 * 100.0,
            "Handicap Asiático Casa (AH -1.0)": p_ah_h_minus10 * 100.0,
            "Handicap Asiático Fora (AH +1.0)": p_ah_a_plus10 * 100.0
        }

        prob_est = market_prob_map.get(market, p_home * 100.0)
        prob_imp = self.calculate_implied_prob(odd)
        ev = self.calculate_ev(prob_est, odd)
        kelly_pct, kelly_stake = self.calculate_kelly_stake(prob_est, odd, bankroll=1000.0, fraction=0.25)

        return {
            "País": country,
            "Liga": league,
            "Jogo": f"{home} vs. {away}",
            "HomeTeam": home,
            "AwayTeam": away,
            "Mercado": market,
            "Odd": round(odd, 2),
            "ExpGoalsHome": round(exp_g_home, 2),
            "ExpGoalsAway": round(exp_g_away, 2),
            "Prob. Implícita (%)": round(prob_imp, 1),
            "Prob. Estimada (%)": round(prob_est, 1),
            "Expected Value (+EV) (%)": ev,
            "KellyStake (%)": kelly_pct,
            "Stake Recomendada (€)": kelly_stake,
            "ProbMatrix": prob_matrix,
            "MarketMap": market_prob_map
        }
