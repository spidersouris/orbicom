import argparse
import glob
import json
import math
import os
import textwrap

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

LANG = "fr"
T = {
    "fr": {
        "lquote": "« ",
        "rquote": " »",
        "surprisal_title": "Surprise associée à la sélection des tokens",
        "tokens_generated": "Tokens générés",
        "surprisal": "Surprise",
        "context": "Contexte",
        "chosen_label": "Choisi :",
        "alt_label": "Alt. :",
        "selection_prob": "Probabilité de sélection :",
        "probability": "Probabilité",
        "threshold": "seuil",
        "and": "et",
    },
    "en": {
        "lquote": '"',
        "rquote": '"',
        "surprisal_title": "Token selection surprisal",
        "tokens_generated": "Step",
        "surprisal": "Surprisal",
        "context": "Context",
        "chosen_label": "Chosen:",
        "alt_label": "Alt:",
        "selection_prob": "Selection probability:",
        "probability": "Probability",
        "threshold": "threshold",
        "and": "and",
    },
}


def load_log_files(folder):
    records = []
    for filename in glob.glob(folder):
        # print(filename)
        if filename.endswith(".jsonl"):
            with open(filename, encoding="utf8") as f:
                for line in f:
                    records.append(json.loads(line.strip()))
    return records


def logprob_to_prob(logprob):
    return math.exp(logprob)


def prob_to_surprisal(prob):
    return -math.log2(prob) if prob > 0 else float("inf")


def extract_pair_data(records, token_pairs, top_k_limit=None, context_window=20):
    data = []
    for record in records:
        step = record["step"]
        chosen_token = record["token"].strip("Ġ▁")
        top_k = {tk["token"].strip("Ġ▁"): tk["logprob"] for tk in record["top_k"]}

        # limit top_k to top_k_limit
        if top_k_limit is not None:
            top_k = dict(
                sorted(top_k.items(), key=lambda item: item[1], reverse=True)[
                    :top_k_limit
                ]
            )

        # extract context (preceding tokens)
        context = record.get("context", "")
        recent_context = " ".join(context.split()[-context_window:]) if context else ""

        for pair in token_pairs:
            for key, value in pair.items():
                has_key = key in top_k
                has_value = value in top_k

                if has_key or has_value:
                    entry = {
                        "step": step,
                        "pair_key": key,
                        "pair_value": value,
                        "chosen_token": chosen_token,
                        "key_logprob": top_k.get(key, None),
                        "value_logprob": top_k.get(value, None),
                        "chosen_logprob": record["logprob"],
                        "recent_context": recent_context,
                    }

                    if chosen_token in [key, value]:
                        entry["chosen_type"] = "key" if chosen_token == key else "value"
                        entry["chosen_prob"] = logprob_to_prob(record["logprob"])
                        entry["surprisal"] = prob_to_surprisal(entry["chosen_prob"])
                    else:
                        entry["chosen_type"] = None

                    data.append(entry)
    return pd.DataFrame(data)


def calculate_confidence_metrics(df):
    """Calculate confidence metrics for pronoun selection"""
    if df.empty:
        return df

    df_with_probs = df.copy()

    # calculate probabilities if not already present
    if "key_prob" not in df_with_probs.columns:
        df_with_probs["key_prob"] = df_with_probs["key_logprob"].apply(
            lambda x: logprob_to_prob(x) if pd.notna(x) else 0
        )

    if "value_prob" not in df_with_probs.columns:
        df_with_probs["value_prob"] = df_with_probs["value_logprob"].apply(
            lambda x: logprob_to_prob(x) if pd.notna(x) else 0
        )

    # confidence as normalized probability
    def calculate_confidence(row):
        if pd.isna(row["chosen_type"]):
            return None

        total_prob = row["key_prob"] + row["value_prob"]
        if total_prob <= 0:
            return 0

        if row["chosen_type"] == "key":
            return row["key_prob"] / total_prob
        else:  # "value"
            return row["value_prob"] / total_prob

    df_with_probs["confidence"] = df_with_probs.apply(calculate_confidence, axis=1)

    # ratio of chosen to alternative
    def calculate_ratio_score(row):
        if pd.isna(row["chosen_type"]):
            return None

        if row["chosen_type"] == "key":
            alt_prob = row["value_prob"]
            chosen_prob = row["key_prob"]
        else:  # "value"
            alt_prob = row["key_prob"]
            chosen_prob = row["value_prob"]

        if alt_prob <= 0:
            return float("inf")
        return chosen_prob / alt_prob

    df_with_probs["ratio_score"] = df_with_probs.apply(calculate_ratio_score, axis=1)

    return df_with_probs


def plot_surprisal_context(
    dfs,
    min_ratio,
    surprisal_threshold=4,
    save_to_file=False,
    save_interactive=False,
):
    fig = make_subplots(
        rows=1,
        cols=3,
        subplot_titles=[
            "<b>Llama-3.2-3B</b>",
            "<b>Mistral-7B-Instruct-v0.3</b>",
            "<b>Qwen2.5-7B-Instruct</b>",
        ],
    )

    for idx, df in enumerate(dfs):
        if df.empty:
            print("Empty dataframe, nothing to plot")
            return

        df = calculate_confidence_metrics(df)

        row = 1
        col = idx + 1

        filtered = df[
            df["key_logprob"].notna()
            & df["value_logprob"].notna()
            & df["chosen_type"].isin(["key", "value"])
        ].copy()

        if filtered.empty:
            print("No valid data points after filtering")
            return

        def meets_ratio(row):
            if row["chosen_type"] == "key":
                return row["value_prob"] >= min_ratio * row["key_prob"]
            elif row["chosen_type"] == "value":
                return row["key_prob"] >= min_ratio * row["value_prob"]
            return False

        filtered = filtered[filtered.apply(meets_ratio, axis=1)]
        if filtered.empty:
            print("No data points meet the minimum ratio requirement")
            return

        key_token = filtered["pair_key"].iloc[0]
        value_token = filtered["pair_value"].iloc[0]

        colors = {
            key_token: "#E69F00",
            value_token: "#56B4E9",
        }

        filtered = filtered[filtered["surprisal"] > surprisal_threshold]
        # print(filtered)

        for chosen_label, alt_label in [("key", "value"), ("value", "key")]:
            chosen_subset = filtered[filtered["chosen_type"] == chosen_label]

            if chosen_subset.empty:
                continue

            token_name = key_token if chosen_label == "key" else value_token
            alt_token_name = value_token if chosen_label == "key" else key_token

            steps = chosen_subset["step"]
            surprisal = chosen_subset["surprisal"]
            context = chosen_subset["recent_context"].apply(
                lambda t: "<br>".join(textwrap.wrap(t))
            )

            fig.add_trace(
                go.Scatter(
                    x=steps,
                    y=surprisal,
                    mode="markers",
                    name=f"{T[LANG]['chosen_label']}: {token_name}",
                    # name=f"Choisi : {token_name}",
                    marker=dict(color=colors[token_name], size=5, opacity=1),
                    hovertemplate=f"{T[LANG]['context']} %{{customdata}}<br>{T[LANG]['surprisal']}: %{{y:.2f}}<extra></extra>",
                    # hovertemplate="Context: %{customdata}<br>Surprisal: %{y:.2f}<extra></extra>",
                    customdata=context,
                ),
                col=col,
                row=row,
            )

    names = set()
    fig.for_each_trace(
        lambda trace: (
            trace.update(showlegend=False)
            if (trace.name in names)
            else names.add(trace.name)
        )
    )

    for col in range(1, 4):
        fig.update_yaxes(
            title_text=T[LANG]["surprisal"],
            gridcolor="lightgray",
            showticklabels=True,
            matches="y",
            row=row,
            col=col,
        )

        fig.update_xaxes(
            title_text=T[LANG]["tokens_generated"],
            gridcolor="lightgray",
            showticklabels=True,
            row=row,
            col=col,
        )

    fig.update_layout(
        height=800,
        width=1600,
        barmode="overlay",
        showlegend=True,
        template="plotly_white",
        legend=dict(
            orientation="h",
            x=1.0,
            y=1.1,
            xanchor="right",
            yanchor="top",
        ),
        title=f"{T[LANG]['surprisal_title']} {T[LANG]['lquote']}{key_token}{T[LANG]['rquote']} {T[LANG]['and']} {T[LANG]['lquote']}{value_token}{T[LANG]['rquote']}, {T[LANG]['threshold']} {round(surprisal_threshold, 2)}",
        # title=f"Surprise associée à la sélection des tokens « {key_token} » et « {value_token} »",
        xaxis_title=f"{T[LANG]['tokens_generated']}",
        yaxis_title=f"{T[LANG]['surprisal']}",
        font=dict(family="Arial", size=14, color="#7f7f7f"),
        paper_bgcolor="white",
        plot_bgcolor="white",
    )

    # fig.update_yaxes(
    # autorange=True,
    # title_text="Probabilité",
    # gridcolor="lightgray"
    # )

    if save_interactive:
        os.makedirs("plots/surprisal", exist_ok=True)
        fig.write_html(
            f"plots/surprisal/surprisal_interactive_{round(surprisal_threshold, 2)}.html",
            include_plotlyjs="cdn",
        )
        print(
            f"Interactive surprisal plot saved to plots/surprisal/surprisal_interactive_{round(surprisal_threshold, 2)}.html"
        )

    if save_to_file:
        os.makedirs("plots/surprisal", exist_ok=True)
        fig.write_image(
            f"plots/surprisal/surprisal_{round(surprisal_threshold, 2)}.svg",
            scale=1.8,
            format="svg",
        )
        print(
            f"Surprisal plot saved to plots/surprisal/surprisal_{round(surprisal_threshold, 2)}.svg"
        )
    else:
        fig.show()


def plot_pair_probabilities(
    dfs,
    min_ratio,
    top_k_limit=None,
    save_to_file=False,
):
    fig = make_subplots(
        rows=1,
        cols=3,
        subplot_titles=[
            "<b>Llama-3.2-3B</b>",
            "<b>Mistral-7B-Instruct-v0.3</b>",
            "<b>Qwen2.5-7B-Instruct</b>",
        ],
    )

    for idx, df in enumerate(dfs):
        if df.empty:
            print("Empty dataframe, nothing to plot")
            return

        df = calculate_confidence_metrics(df)

        row = 1
        col = idx + 1

        filtered = df[
            df["key_logprob"].notna()
            & df["value_logprob"].notna()
            & df["chosen_type"].isin(["key", "value"])
        ].copy()

        # filtered.to_csv(f"{idx}.csv")

        if filtered.empty:
            print("No valid data points after filtering")
            return

        def meets_ratio(row):
            if row["chosen_type"] == "key":
                return row["value_prob"] >= min_ratio * row["key_prob"]
            elif row["chosen_type"] == "value":
                return row["key_prob"] >= min_ratio * row["value_prob"]
            return False

        filtered = filtered[filtered.apply(meets_ratio, axis=1)]
        if filtered.empty:
            print("No data points meet the minimum ratio requirement")
            return

        key_token = filtered["pair_key"].iloc[0]
        value_token = filtered["pair_value"].iloc[0]

        colors = {
            key_token: "#E69F00",
            value_token: "#56B4E9",
        }

        for chosen_label, alt_label in [("key", "value"), ("value", "key")]:
            chosen_subset = filtered[filtered["chosen_type"] == chosen_label]

            if chosen_subset.empty:
                continue

            token_name = key_token if chosen_label == "key" else value_token
            alt_token_name = value_token if chosen_label == "key" else key_token

            steps = chosen_subset["step"]
            probs = chosen_subset[f"{chosen_label}_prob"]
            alt_probs = chosen_subset[f"{alt_label}_prob"]

            # comparison_mask = alt_probs >= probs
            # print(
            #     f"Percentage of cases where alt_prob >= prob for {chosen_label}:",
            #     comparison_mask.mean(),
            # )
            # print(
            #     f"Total cases: {len(probs)}, Matches: {comparison_mask.sum()}, Non-matches: {(~comparison_mask).sum()}"
            # )

            fig.add_trace(
                go.Scatter(
                    x=steps,
                    y=probs,
                    mode="markers",
                    name=f"{T[LANG]['chosen_label']} {token_name}",
                    marker=dict(color=colors[token_name], size=5, opacity=1),
                ),
                col=col,
                row=row,
            )

            fig.add_trace(
                go.Bar(
                    x=steps,
                    y=alt_probs,
                    width=8,
                    name=(
                        f"{T[LANG]['alt_label']} {alt_token_name}"
                        if token_name == key_token
                        else f"{T[LANG]['alt_label']} {key_token}"
                    ),
                    marker=dict(color=colors[alt_token_name], opacity=0.5),
                ),
                col=col,
                row=row,
            )

    names = set()
    fig.for_each_trace(
        lambda trace: (
            trace.update(showlegend=False)
            if (trace.name in names)
            else names.add(trace.name)
        )
    )

    for col in range(1, 4):
        fig.update_yaxes(
            title_text=f"{T[LANG]['probability']}",
            gridcolor="lightgray",
            showticklabels=True,
            range=[0, 1],
            autorange=False,
            matches="y",
            row=row,
            col=col,
        )

        fig.update_xaxes(
            title_text=f"{T[LANG]['tokens_generated']}",
            gridcolor="lightgray",
            showticklabels=True,
            row=row,
            col=col,
        )

    fig.update_layout(
        height=800,
        width=1600,
        barmode="overlay",
        showlegend=True,
        template="plotly_white",
        legend=dict(
            orientation="h",
            x=1.0,
            y=1.1,
            xanchor="right",
            yanchor="top",
        ),
        title=f"{T[LANG]['selection_prob']} {T[LANG]['lquote']}{key_token}{T[LANG]['rquote']} {T[LANG]['and']} {T[LANG]['lquote']}{value_token}{T[LANG]['rquote']}, top_k {top_k_limit if top_k_limit else 'MISSING TOPK'}, {T[LANG]['threshold']} {round(min_ratio, 4)}",
        # title=f"Probabilité de sélection : « {key_token} » et « {value_token} », top_k {top_k_limit if top_k_limit else 'MISSING TOPK'}, seuil {round(min_ratio, 4)}",
        xaxis_title=f"{T[LANG]['tokens_generated']}",
        yaxis_title=f"{T[LANG]['probability']}",
        font=dict(family="Arial", size=14, color="#7f7f7f"),
        title_font_color="red" if top_k_limit is None else "#7f7f7f",
        paper_bgcolor="white",
        plot_bgcolor="white",
    )

    # fig.update_yaxes(
    # autorange=True,
    # title_text="Probabilité",
    # gridcolor="lightgray"
    # )

    if save_to_file:
        os.makedirs(f"plots/probs/k{top_k_limit}/", exist_ok=True)
        fig.write_image(
            f"plots/probs/k{top_k_limit}/probs_{round(min_ratio, 4)}.svg",
            scale=1.8,
            format="svg",
        )
        print(
            f"Probabilities plot saved to plots/probs/k{top_k_limit}/probs_{round(min_ratio, 4)}.svg"
        )

    # fig.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Plot logprobs and surprisal")
    parser.add_argument(
        "token1",
        type=str,
        help="First token to analyze",
    )
    parser.add_argument(
        "token2",
        type=str,
        help="Second token to analyze",
    )
    parser.add_argument(
        "-l",
        "--level",
        type=str,
        choices=["ce1", "cm1", "all"],
        required=True,
        help="Level of the corpus ('ce1' or 'cm1' or 'all' for both levels)",
    )
    parser.add_argument(
        "-t",
        "--text_type",
        type=str,
        choices=["literature", "scientific", "all"],
        required=True,
        help="Type of text from the corpus ('literature' or 'scientific' or 'all' for both types)",
    )
    parser.add_argument(
        "-g",
        "--gen_type",
        type=str,
        choices=["continuation", "generation", "all"],
        required=True,
        help="Type of generation ('continuation', 'generation', or 'all' for both types)",
    )
    parser.add_argument(
        "-r",
        "--min_ratio",
        type=float,
        default=1 / 3,
        help="(probs/surprisal) Minimum ratio of value to key probability for inclusion in the plot (default: 1/3)",
    )
    parser.add_argument(
        "-k",
        "--top_k_limit",
        type=int,
        default=None,
        help="(probs) Limit for top-k alternatives. If None, no limit is applied (default: None)",
    )
    parser.add_argument(
        "-c",
        "--context_window",
        type=int,
        default=20,
        help="(surprisal, HTML) Context window size of preceding tokens (default: 20)",
    )
    parser.add_argument(
        "-s",
        "--surprisal_threshold",
        type=float,
        default=4.0,
        help="(surprisal) Surprisal threshold for filtering (default: 4.0)",
    )
    parser.add_argument(
        "--lang",
        type=str,
        default="fr",
        choices=["fr", "en"],
        help="Language of the plots (default: 'fr')",
    )
    parser.add_argument(
        "-svg",
        "--save_svg",
        action="store_true",
        help="Save plot as SVG",
    )
    parser.add_argument(
        "-html",
        "--save_html",
        action="store_true",
        help="(surprisal) Save an interactive HTML plot",
    )
    args = parser.parse_args()

    list_dfs = []

    token_pairs = [{args.token1: args.token2}]
    level_plot = args.level
    task_plot = args.gen_type
    text_type_plot = args.text_type

    model_map = {
        "llama": "Llama-3.2-3B",
        "mistral": "Mistral-7B-Instruct-v0.3",
        "qwen": "Qwen2.5-7B-Instruct",
    }

    if level_plot == "all":
        level_plot = "*"

    if task_plot == "all":
        task_plot = "*"

    if args.text_type == "all":
        text_type_plot = "*"

    LANG = args.lang

    for k, v in model_map.items():
        log_folder = (
            f"results/{v}/{level_plot}/{text_type_plot}/{task_plot}/logits/*.jsonl"
        )
        records = load_log_files(log_folder)
        df = extract_pair_data(
            records,
            token_pairs,
            top_k_limit=args.top_k_limit,
            context_window=args.context_window,
        )
        list_dfs.append(df)

    plot_pair_probabilities(
        list_dfs,
        min_ratio=args.min_ratio,
        top_k_limit=args.top_k_limit,
        save_to_file=args.save_svg,
    )

    plot_surprisal_context(
        list_dfs,
        min_ratio=args.min_ratio,
        surprisal_threshold=args.surprisal_threshold,
        save_to_file=args.save_svg,
        save_interactive=args.save_html,
    )
