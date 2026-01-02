#
# Space Leaf Corp — Stewardship Header
# Seal of No In‑Between 1.0 — God’s Children Edition
# Seal of Dual Authentication 1.0 — Body and Badge Edition
# Seal of Stand and Speak 1.0 — Embodied Stewardship Edition
#
# This file is part of a lineage‑safe project dedicated to planetary care,
# educational uplift, and the protection of all children — microscopic or otherwise.
#
# By modifying or distributing this file, you agree to uphold the principles
# of the Space Leaf Corp Open Stewardship License 1.0.
#
# May your work travel safely.

# utils.py

import os
try:
    import numpy as np  # type: ignore
except ImportError:
    np = None
from typing import Any, Optional, Dict

def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)

def plot_timeseries(df, col, title=None, ylabel=None): # pyright: ignore[reportUnknownParameterType, reportMissingParameterType]
    try:
        import matplotlib.pyplot as plt # pyright: ignore[reportMissingModuleSource]
    except ImportError:
        raise ImportError("matplotlib is not installed. Plotting functions will not work.")
    fig, ax = plt.subplots(figsize=(10,4))  # type: ignore
    ax.plot(df["t_day"], df[col], lw=1)  # type: ignore
    ax.set_xlabel("Time day")  # pyright: ignore[reportUnknownMemberType]
    # Ensure ylabel is always a string to avoid type issues
    # Ensure ylabel and col are always strings to avoid type issues
    if ylabel is not None:
        label_str: str = str(ylabel) # pyright: ignore[reportUnknownArgumentType]
    else:
        label_str: str = str(col) # pyright: ignore[reportUnknownArgumentType]
    ax.set_ylabel(label_str)  # type: ignore[reportUnknownMemberType]
    ax.set_title(title or col)  # type: ignore[reportUnknownMemberType]
    ax.grid(True, which="both", axis="both", alpha=0.3)  # type: ignore
    return fig

try:
    import pandas as pd  # type: ignore
except ImportError:
    pd = None

def summarize_run(
    df: Any,  # type: ignore
    flips: int,
    recon_events: int,
    params: Any,
    T_days: float
) -> Dict[str, Optional[float]]:
    if pd is None:
        raise ImportError("pandas is not installed. DataFrame functions will not work.")
        
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")
    # Ensure T_days is a float
    T_days = float(T_days)
    # Use pandas methods directly to avoid type issues
    if np is not None:
        maxK = float(np.array(df["K"], dtype=float).max())  # type: ignore
    else:
        maxK = float(max([float(x) for x in df["K"]]))
    if T_days >= 365:
        if np is not None:
            mean_first_year = float(np.mean(np.array(df[df["t_day"] < 365.0]["K"], dtype=float)))  # type: ignore
            last_year_start = max(0.0, T_days - 365.0)
            mean_last_year = float(np.mean(np.array(df[df["t_day"] >= last_year_start]["K"], dtype=float)))  # type: ignore
        else:
            mean_first_year = float(sum([float(x) for x in df[df["t_day"] < 365.0]["K"]]) / max(1, len(df[df["t_day"] < 365.0]["K"])))
            last_year_start = max(0.0, T_days - 365.0)
            mean_last_year = float(sum([float(x) for x in df[df["t_day"] >= last_year_start]["K"]]) / max(1, len(df[df["t_day"] >= last_year_start]["K"])))
    else:
        if np is not None:
            mean_first_year = float(np.mean(np.array(df["K"], dtype=float)))  # type: ignore
        else:
            mean_first_year = float(sum([float(x) for x in df["K"]]) / max(1, len(df["K"])))
        mean_last_year = mean_first_year
    secular_change = None
    if T_days >= 365:
        secular_change = (mean_last_year - mean_first_year) / (mean_first_year + 1e-12) * 100.0
    verdict = "GO"
    if maxK >= 10.0:
        verdict = "NO-GO: runaway K"
    if recon_events > 0 and recon_events > 0.2 * (T_days / 1.0):
        verdict = "NO-GO: excessive reconnection"
    summary: Dict[str, Optional[float]] = {
        "maxK": maxK,
        "flips": flips,
        "reconnection_events": recon_events,
        "meanK_first_year": mean_first_year,
        "meanK_last_year": mean_last_year,
        "secular_change_percent": secular_change,
        "verdict": verdict  # type: ignore
    }
    return summary # pyright: ignore[reportUnknownVariableType]


# Example usage to ensure plot_timeseries is accessed
if __name__ == "__main__":
    if pd is not None:
        # Create a simple DataFrame for demonstration
        if np is not None:
            t_day: "np.ndarray" = np.arange(10)  # type: ignore
            k_values = np.random.rand(10)  # type: ignore
        else:
            import random  # pyright: ignore[reportUnknownMemberType]
            t_day = list(range(10))
            k_values: Any = [random.random() for _ in range(10)]  # type: ignore
        df = pd.DataFrame({
            "t_day": t_day,
            "K": k_values
        })
        try:
            fig = plot_timeseries(df, "K", title="Demo Plot", ylabel="K value")
            # Optionally show or save the plot
            # fig.show()
        except ImportError:
            print("matplotlib not installed; skipping plot.")

